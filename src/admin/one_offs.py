import datetime
import webapp2

from src.models import Competitor
from src.models import Group
from src.models import StaffAssignment

def CloneAssignment(assignment, new_id):
  new_assignment = StaffAssignment(id = assignment.key.id().replace('533', '277'))
  new_assignment.group = assignment.group
  if assignment.long_event:
    new_assignment.long_event = assignment.long_event
  new_assignment.staff_member = assignment.staff_member
  new_assignment.job = assignment.job
  if assignment.station:
    new_assignment.station = assignment.station
  if assignment.misc:
    new_assignment.misc = assignment.misc
  return new_assignment
  

class OneOffHandler(webapp2.RequestHandler):
  def get(self, name):
    futures = []
    if name == 'garrett':
      # Give all of Nathan Dwyer's judging jobs on Friday and Saturday to Garrett Webster.
      garrett = Competitor.get_by_id('277')
      nathan = Competitor.get_by_id('533')
      sunday_start = datetime.datetime(2017, 7, 9, 0, 0, 0)
      for assignment in StaffAssignment.query(StaffAssignment.staff_member == nathan.key).iter():
        if assignment.group.get().start_time > sunday_start:
          continue
        new_assignment = CloneAssignment(assignment, assignment.key.id().replace('533', '277'))
        new_assignment.staff_member = garrett.key
        futures.append(assignment.key.delete_async())
        futures.append(new_assignment.put_async())
    elif name == 'dimitri':
      # Dimitri Dennis cancelled.  Give his Friday+Saturday jobs to Nathan, and give his Sunday jobs to Shelley.
      dimitri = Competitor.get_by_id('215')
      nathan = Competitor.get_by_id('533')
      shelley = Competitor.get_by_id('678')
      sunday_start = datetime.datetime(2017, 7, 9, 0, 0, 0)
      for assignment in StaffAssignment.query(StaffAssignment.staff_member == dimitri.key).iter():
        if assignment.group.get().start_time > sunday_start:
          new_assignment = CloneAssignment(assignment, assignment.key.id().replace('215', '678'))
          new_assignment.staff_member = shelley.key
        else:
          new_assignment = CloneAssignment(assignment, assignment.key.id().replace('215', '533'))
          new_assignment.staff_member = nathan.key
        futures.append(assignment.key.delete_async())
        futures.append(new_assignment.put_async())
    elif name == '333oh_3':
      # Blue stage pyra round 3 should really be OH round 3.
      oh_groups = [Group.get_by_id(Group.Id('333oh', 3, 'b', num)) for num in [1, 2, 3]]
      pyram_groups = [Group.get_by_id(Group.Id('pyram', 3, 'b', num)) for num in [1, 2, 3]]
      for oh_group, pyram_group in zip(oh_groups, pyram_groups):
        for assignment in StaffAssignment.query(StaffAssignment.group == pyram_group.key).iter():
          assignment.group = oh_group.key
          futures.append(assignment.put_async())
        for assignment in StaffAssignment.query(StaffAssignment.group == oh_group.key):
          new_assignment = CloneAssignment(assignment, assignment.key.id().replace('pyram', '333oh'))
          futures.append(assignment.key.delete_async())
          futures.append(new_assignment.put_async())
    elif name == 'staff_group_numbers':
      # Groups numbered -1 should be numbered 0 instead.
      wrong_groups = [Group.get_by_id(Group.Id(event, 2, stage, -1)) for event in ['333oh', 'skewb', '222'] for stage in ['r', 'b', 'g', 'o']]
      right_groups = [Group.get_by_id(Group.Id(event, 2, stage, 0)) for event in ['333oh', 'skewb', '222'] for stage in ['r', 'b', 'g', 'o']]
      for wrong_group, right_group in zip(wrong_groups, right_groups):
        for assignment in StaffAssignment.query(StaffAssignment.group == wrong_group.key).iter():
          new_assignment = CloneAssignment(assignment, assignment.key.id().replace('-1', '0'))
          new_assignment.group = right_group.key
          futures.append(assignment.key.delete_async())
          futures.append(new_assignment.put_async())
    elif name == 'extra_C':
      # accidentally assigned jobs called "C 5", these don't exist.
      for assignment in (StaffAssignment.query()
                                        .filter(StaffAssignment.job.IN(["C 5", "C 4", "C sq1",  "C 3", "C 2", "C pyra"]))
                                        .iter()):
        futures.append(assignment.key.delete_async())
    for future in futures:
      future.get_result()
