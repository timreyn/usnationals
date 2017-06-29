import webapp2

from src.models import Competitor
from src.models import Heat
from src.models import StaffAssignment

class OneOffHandler(webapp2.RequestHandler):
  def get(self, name):
    futures = []
    if name == 'garrett':
      # Give all of Nathan Dwyer's judging jobs to Garrett Webster.
      garrett = Competitor.get_by_id('277')
      nathan = Competitor.get_by_id('533')
      for assignment in StaffAssignment.query(StaffAssignment.staff_member == nathan.key).iter():
        assignment.staff_member = garrett.key
        futures.append(assignment.put_async())
      for assignment in StaffAssignment.query(StaffAssignment.staff_member == garrett.key).iter():
        new_assignment = StaffAssignment(id = assignment.key.id().replace('533', '277'))
        new_assignment.heat = assignment.heat
        if assignment.long_event:
          new_assignment.long_event = assignment.long_event
        new_assignment.staff_member = assignment.staff_member
        new_assignment.job = assignment.job
        if assignment.station:
          new_assignment.station = assignment.station
        if assignment.misc:
          new_assignment.misc = assignment.misc
        futures.append(assignment.key.delete_async())
        futures.append(new_assignment.put_async())
    elif name == '333oh_3':
      # Blue stage pyra round 3 should really be OH round 3.
      oh_heats = [Heat.get_by_id(Heat.Id('333oh', 3, 'b', num)) for num in [1, 2, 3]]
      pyram_heats = [Heat.get_by_id(Heat.Id('pyram', 3, 'b', num)) for num in [1, 2, 3]]
      for oh_heat, pyram_heat in zip(oh_heats, pyram_heats):
        for assignment in StaffAssignment.query(StaffAssignment.heat == pyram_heat.key).iter():
          assignment.heat = oh_heat.key
          futures.append(assignment.put_async())
        for assignment in StaffAssignment.query(StaffAssignment.heat == oh_heat.key):
          new_assignment = StaffAssignment(id = assignment.key.id().replace('pyram', '333oh'))
          new_assignment.heat = assignment.heat
          if assignment.long_event:
            new_assignment.long_event = assignment.long_event
          new_assignment.staff_member = assignment.staff_member
          new_assignment.job = assignment.job
          if assignment.station:
            new_assignment.station = assignment.station
          if assignment.misc:
            new_assignment.misc = assignment.misc
          futures.append(assignment.key.delete_async())
          futures.append(new_assignment.put_async())
    for future in futures:
      future.get_result()
