import collections
import csv
import datetime
import StringIO
import webapp2

from google.appengine.ext import ndb

from src.jinja import JINJA_ENVIRONMENT
from src.models import Competitor
from src.models import Heat
from src.models import HeatAssignment
from src.models import Round
from src.models import StaffAssignment

class AssignHeats(webapp2.RequestHandler):
  def get(self):
    self.response.write(self.MainTemplate().render({
        'path': webapp2.uri_for('assign_heats'),
        'rounds': self.GetAllRounds(),
    }))

  def post(self):
    round_id = self.request.get('r')
    if not round_id:
      self.response.write(self.MainTemplate().render({
          'unknown_round': '(missing)',
          'path': webapp2.uri_for('assign_heats'),
          'rounds': self.GetAllRounds(),
      }))
      return
    r = Round.get_by_id(round_id)
    if not r:
      self.response.write(self.MainTemplate().render({
          'unknown_round': round_id,
          'path': webapp2.uri_for('assign_heats'),
          'rounds': self.GetAllRounds(),
      }))
      return
    if self.request.get('submit_heats'):
      self.SubmitHeats(r)
    else:
      self.ComputeHeats(r)

  def ComputeHeats(self, r):
    memfile = StringIO.StringIO(self.request.get('ids'))
    competitors = []
    competitor_ids = set()
    for row in csv.reader(memfile):
      if not row:
        continue
      c = Competitor.get_by_id(row[0])
      if not c:
        self.response.write(self.MainTemplate().render({
            'unknown_competitor': row,
            'path': webapp2.uri_for('assign_heats'),
            'rounds': self.GetAllRounds(),
        }))
        return
      competitors.append(c)
      competitor_ids.add(c.key.id())
    competitor_to_conflicting_heats = collections.defaultdict(list)
    round_heats = [h for h in Heat.query(Heat.round == r.key).iter()]
    round_heat_keys = [h.key for h in round_heats]
    beginning = min([h.start_time for h in round_heats])
    end = max([h.end_time for h in round_heats])
    conflicting_heats = [h for h in Heat.query()
                                        .filter(Heat.start_time >= beginning)
                                        .iter()
                         if h.end_time < end and h.round != r.key]
    for assignment in (
          HeatAssignment.query()
                        .filter(HeatAssignment.competitor.IN([c.key for c in competitors]))
                        .filter(HeatAssignment.heat.IN([h.key for h in conflicting_heats]))
                        .iter()):
      competitor_to_conflicting_heats[assignment.competitor.id()].append((h, "C"))
    for assignment in (
          StaffAssignment.query()
                         .filter(StaffAssignment.staff_member.IN([c.key for c in competitors]))
                         .filter(StaffAssignment.heat.IN([h.key for h in conflicting_heats + round_heats]))
                         .iter()):
      competitor_to_conflicting_heats[assignment.staff_member.id()].append((h, assignment.job))

    competitor_to_valid_heats = collections.defaultdict(set)
    for competitor in competitors:
      conflicting_heats = competitor_to_conflicting_heats[competitor.key.id()]
      for heat in round_heats:
        valid = True
        for conflicting_heat, _ in conflicting_heats:
          if (conflicting_heat.start_time < heat.end_time and
              conflicting_heat.end_time > heat.start_time):
            valid = False
            break
        if valid:
          competitor_to_valid_heats[competitor.key.id()].add(heat.key.id())

    # Now assign heats.
    assignments = {}
    i = 0
    for heat in sorted(round_heats, key=lambda heat: heat.number):
      num_competitors = len(competitors) / len(round_heats)
      if i < len(competitors) % len(round_heats):
        num_competitors += 1
      i += 1
      # Check for people who can only be in this heat.
      for competitor in competitors:
        valid_heats = competitor_to_valid_heats[competitor.key.id()]
        if competitor.key.id() not in assignments and len(valid_heats) == 1 and heat.key.id() in valid_heats:
          assignments[competitor.key.id()] = heat
          num_competitors -= 1
      # Now everyone else.
      for competitor in reversed(competitors):
        if num_competitors <= 0:
          break
        if competitor.key.id() not in assignments and heat.key.id() in competitor_to_valid_heats[competitor.key.id()]:
          assignments[competitor.key.id()] = heat
          num_competitors -= 1
      # And now this heat is invalid for everyone.
      for heats in competitor_to_valid_heats.itervalues():
        heats.discard(heat.key.id())

    # Check if there are already competitors.
    num_current_competitors = 0
    for h in HeatAssignment.query().iter():
      if h.heat in round_heat_keys:
        num_current_competitors += 1
    
    self.response.write(self.AssigningTemplate().render({
        'round': r,
        'num_current_competitors': num_current_competitors,
        'competitors': competitors,
        'round_heats': round_heats,
        'format': '%I:%M %p',
        'assignments': assignments,
        'competitor_to_conflicting_heats': competitor_to_conflicting_heats,
        'path': webapp2.uri_for('assign_heats'),
    }))

  def SubmitHeats(self, r):
    # Delete old values.
    round_heat_keys = [h.key for h in Heat.query(Heat.round == r.key).iter()]
    ndb.delete_multi(HeatAssignment.query()
                        .filter(HeatAssignment.heat.IN(round_heat_keys))
                        .iter(keys_only=True))
    # Add values.
    event = r.event.get()
    round_heats = {h.key.id() : h for h in Heat.query(Heat.round == r.key).iter()}
    for key, value in self.request.POST.iteritems():
      if key.startswith('c_'):
        competitor_id = key[2:]
        assignment = HeatAssignment(id = HeatAssignment.Id(event.key.id(), r.number, competitor_id))
        if value not in round_heats:
          self.response.write('Couldn\'t find heat %s' % value)
          continue
        assignment.heat = round_heats[value].key
        assignment.competitor = ndb.Key(Competitor, competitor_id)
        assignment.put()
    self.response.write('Success!')
        
  def MainTemplate(self):
    return JINJA_ENVIRONMENT.get_template('assign_heats.html')

  def AssigningTemplate(self):
    return JINJA_ENVIRONMENT.get_template('assign_heats_2.html')

  def GetAllRounds(self):
    return [r for r in Round.query(Round.number > 1).iter()]
