from src import common
from src.jinja import JINJA_ENVIRONMENT
from src.admin.assignments import formats
from src.models import Competitor
from src.models import DebugInfo
from src.models import EventRegistration
from src.models import Heat
from src.models import Round

import collections
import json
import webapp2

class SortByCompetitorTime(object):
  def __init__(self, reg_list, should_use_average):
    self.reg_list = reg_list
    self.should_use_average = should_use_average

  def __call__(self, c):
    if c.key.id() not in self.reg_list:
      return '60000'
    if self.should_use_average:
      return self.reg_list[c.key.id()].average
    else:
      return self.reg_list[c.key.id()].single

class AssignmentsDebugHandler(webapp2.RequestHandler):
  def get(self, request_id):
    debug_info = DebugInfo.get_by_id(request_id)
    if not debug_info:
      self.response.write('Couldn\'t find results from heat assignment.  Check back in a few seconds!')
      return
    deb = json.loads(debug_info.info)

    template = JINJA_ENVIRONMENT.get_template('assign_heats_debug.html')
    
    competitors = [competitor for competitor in Competitor.query().iter()]
    competitor_dict = {c.key.id() : c for c in competitors}
    rounds = [r for r in Round.query().iter() if r.key.id() in deb['r']]
    heat_dict = {h.key.id() : h for h in Heat.query().iter() if h.round.id() in deb['r']}
    heats_by_round = {
      r: [heat_dict[h] for h in hs] for r, hs in deb['r2h'].iteritems()
    }
    for heats in heats_by_round.itervalues():
      heats.sort(key=lambda heat: heat.start_time)
    competitors_by_heat = {
      h: [competitor_dict[c] for c in cs] for h, cs in deb['h2c'].iteritems()
    }
    heats_by_competitor = collections.defaultdict(list)
    for h, cs in competitors_by_heat.iteritems():
      for c in cs:
        heats_by_competitor[c.key.id()].append(heat_dict[h])

    registrations_by_round = collections.defaultdict(dict)
    for r in rounds:
      for reg in EventRegistration.query(EventRegistration.event == r.event).iter():
        registrations_by_round[r.key.id()][reg.competitor.id()] = reg

    for h, competitors in competitors_by_heat.iteritems():
      should_use_average = common.ShouldUseAverage(heat_dict[h].round.get().event.id())
      competitors.sort(key=SortByCompetitorTime(registrations_by_round[heat_dict[h].round.id()], should_use_average))

    self.response.write(template.render({
        'rounds': rounds,
        'heats_by_round': heats_by_round,
        'competitors_by_heat': competitors_by_heat,
        'competitors': competitors,
        'heats_by_competitor': heats_by_competitor,
        'registrations_by_round': registrations_by_round,
        'debug_info': deb['d'],
        'len': len,
        'formats': formats,
    }))
