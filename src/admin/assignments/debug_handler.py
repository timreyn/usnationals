from src import common
from src.jinja import JINJA_ENVIRONMENT
from src.admin.assignments import formats
from src.models import Competitor
from src.models import DebugInfo
from src.models import EventRegistration
from src.models import Group
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
      self.response.write('Couldn\'t find results from group assignment.  Check back in a few seconds!')
      return
    deb = json.loads(debug_info.info)

    template = JINJA_ENVIRONMENT.get_template('assign_groups_debug.html')
    
    competitors = [competitor for competitor in Competitor.query().iter()]
    competitor_dict = {c.key.id() : c for c in competitors}
    rounds = [r for r in Round.query().iter() if r.key.id() in deb['r']]
    group_dict = {h.key.id() : h for h in Group.query().iter() if h.round.id() in deb['r']}
    groups_by_round = {
      r: [group_dict[h] for h in hs] for r, hs in deb['r2h'].iteritems()
    }
    for groups in groups_by_round.itervalues():
      groups.sort(key=lambda group: group.start_time)
    competitors_by_group = {
      h: [competitor_dict[c] for c in cs] for h, cs in deb['h2c'].iteritems()
    }
    groups_by_competitor = collections.defaultdict(list)
    for h, cs in competitors_by_group.iteritems():
      for c in cs:
        groups_by_competitor[c.key.id()].append(group_dict[h])

    registrations_by_round = collections.defaultdict(dict)
    for r in rounds:
      for reg in EventRegistration.query(EventRegistration.event == r.event).iter():
        registrations_by_round[r.key.id()][reg.competitor.id()] = reg

    for h, cs in competitors_by_group.iteritems():
      should_use_average = common.ShouldUseAverage(group_dict[h].round.get().event.id())
      cs.sort(key=SortByCompetitorTime(registrations_by_round[group_dict[h].round.id()], should_use_average))

    self.response.write(template.render({
        'rounds': rounds,
        'groups_by_round': groups_by_round,
        'competitors_by_group': competitors_by_group,
        'competitors': competitors,
        'groups_by_competitor': groups_by_competitor,
        'registrations_by_round': registrations_by_round,
        'debug_info': deb['d'],
        'desired_competitors_by_round': deb['r2n'],
        'len': len,
        'formats': formats,
    }))
