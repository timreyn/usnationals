import collections
import csv
import datetime
import StringIO
import webapp2

from google.appengine.ext import ndb

from src.jinja import JINJA_ENVIRONMENT
from src.models import Competitor
from src.models import Group
from src.models import GroupAssignment
from src.models import Round
from src.models import StaffAssignment

class AssignGroups(webapp2.RequestHandler):
  def get(self):
    self.response.write(self.MainTemplate().render({
        'path': webapp2.uri_for('assign_groups'),
        'rounds': self.GetAllRounds(),
    }))

  def post(self):
    round_id = self.request.get('r')
    if not round_id:
      self.response.write(self.MainTemplate().render({
          'unknown_round': '(missing)',
          'path': webapp2.uri_for('assign_groups'),
          'rounds': self.GetAllRounds(),
      }))
      return
    r = Round.get_by_id(round_id)
    if not r:
      self.response.write(self.MainTemplate().render({
          'unknown_round': round_id,
          'path': webapp2.uri_for('assign_groups'),
          'rounds': self.GetAllRounds(),
      }))
      return
    if self.request.get('submit_groups'):
      self.SubmitGroups(r)
    else:
      self.ComputeGroups(r)

  def ComputeGroups(self, r):
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
            'path': webapp2.uri_for('assign_groups'),
            'rounds': self.GetAllRounds(),
        }))
        return
      competitors.append(c)
      competitor_ids.add(c.key.id())

    if r.is_final and r.key.id() != '333_4':
      competitors = competitors[::2] + competitors[1::2]
    competitor_to_conflicting_groups = collections.defaultdict(list)
    round_groups = [h for h in Group.query(Group.round == r.key).iter()]
    round_group_keys = [h.key for h in round_groups]
    beginning = min([h.start_time for h in round_groups if h.number > 0])
    end = max([h.end_time for h in round_groups if h.number > 0])
    conflicting_groups = [h for h in Group.query()
                                        .filter(Group.end_time > beginning)
                                        .iter()
                         if h.start_time < end and h.round != r.key and h.key.id() != '444bf_1_y_1']
    competitor_to_valid_groups = collections.defaultdict(set)
    if conflicting_groups:
      for assignment in (
           GroupAssignment.query().filter(GroupAssignment.group.IN([h.key for h in conflicting_groups])).iter()):
        if assignment.competitor.id() in competitor_ids:
          competitor_to_conflicting_groups[assignment.competitor.id()].append((assignment.group.get(), "C"))
    if round_groups or conflicting_groups:
      for assignment in (
            StaffAssignment.query()
                           .filter(StaffAssignment.group.IN([h.key for h in conflicting_groups + round_groups])).iter()):
        if assignment.staff_member.id() in competitor_ids:
          competitor_to_conflicting_groups[assignment.staff_member.id()].append((assignment.group.get(), assignment.job))

    has_staff_groups = False
    num_staff_competitors = 0
    num_non_staff_competitors = 0

    for competitor in competitors:
      conflicting_groups = competitor_to_conflicting_groups[competitor.key.id()]
      if competitor.is_staff and has_staff_groups:
        num_staff_competitors += 1
      else:
        num_non_staff_competitors += 1
      for group in round_groups:
        valid = True
        for conflicting_group, _ in conflicting_groups:
          if (conflicting_group.start_time < group.end_time and
              conflicting_group.end_time > group.start_time):
            valid = False
            break
        if valid:
          if has_staff_groups:
            if competitor.is_staff == (group.number == 0):
              competitor_to_valid_groups[competitor.key.id()].add(group.key.id())
          else:
            competitor_to_valid_groups[competitor.key.id()].add(group.key.id())

    # Now assign groups.
    assignments = {}
    i = 0

    for group in sorted(round_groups, key=lambda group: group.number):
      num_competitors_eligible = len(competitors)
      num_groups_eligible = len(round_groups)
      if has_staff_groups:
        if group.number > 0:
          num_competitors_eligible = num_non_staff_competitors
          num_groups_eligible = len(round_groups) - 4
        else:
          num_competitors_eligible = num_staff_competitors
          num_groups_eligible = 4
      num_competitors = num_competitors_eligible / num_groups_eligible
      if i < num_competitors_eligible % num_groups_eligible:
        num_competitors += 1
      i += 1
      # Check for people who can only be in this group.
      for competitor in competitors:
        valid_groups = competitor_to_valid_groups[competitor.key.id()]
        if competitor.key.id() not in assignments and len(valid_groups) == 1 and group.key.id() in valid_groups:
          assignments[competitor.key.id()] = group
          num_competitors -= 1
      # Now everyone else.
      for competitor in reversed(competitors):
        if num_competitors <= 0:
          break
        if competitor.key.id() not in assignments and group.key.id() in competitor_to_valid_groups[competitor.key.id()]:
          assignments[competitor.key.id()] = group
          num_competitors -= 1
      # And now this group is invalid for everyone.
      for groups in competitor_to_valid_groups.itervalues():
        groups.discard(group.key.id())

    # Check if there are already competitors.
    num_current_competitors = 0
    for h in GroupAssignment.query().filter(GroupAssignment.group.IN(round_group_keys)).iter():
      num_current_competitors += 1
    
    self.response.write(self.AssigningTemplate().render({
        'round': r,
        'num_current_competitors': num_current_competitors,
        'competitors': competitors,
        'round_groups': round_groups,
        'format': '%I:%M %p',
        'assignments': assignments,
        'competitor_to_conflicting_groups': competitor_to_conflicting_groups,
        'path': webapp2.uri_for('assign_groups'),
    }))

  def SubmitGroups(self, r):
    # Delete old values.
    round_group_keys = [h.key for h in Group.query(Group.round == r.key).iter()]
    ndb.delete_multi(GroupAssignment.query()
                        .filter(GroupAssignment.group.IN(round_group_keys))
                        .iter(keys_only=True))
    # Add values.
    event = r.event.get()
    round_groups = {h.key.id() : h for h in Group.query(Group.round == r.key).iter()}
    futures = []
    for key, value in self.request.POST.iteritems():
      if key.startswith('c_'):
        competitor_id = key[2:]
        assignment = GroupAssignment(id = GroupAssignment.Id(Round.Id(event.key.id(), r.number), competitor_id))
        if value not in round_groups:
          self.response.write('Couldn\'t find group %s' % value)
          continue
        assignment.group = round_groups[value].key
        assignment.competitor = ndb.Key(Competitor, competitor_id)
        futures.append(assignment.put_async())
    for future in futures:
      future.get_result()
    self.response.write('Success!')
        
  def MainTemplate(self):
    return JINJA_ENVIRONMENT.get_template('assign_groups.html')

  def AssigningTemplate(self):
    return JINJA_ENVIRONMENT.get_template('assign_groups_2.html')

  def GetAllRounds(self):
    return [r for r in Round.query(Round.number > 1).iter()]
