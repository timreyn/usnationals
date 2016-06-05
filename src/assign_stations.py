import collections
import random
import webapp2

from src.models import StaffAssignment

class AssignStations(webapp2.RequestHandler):
  def get(self):
    staff_assignments = StaffAssignment.query(StaffAssignment.job == "J").iter()
    assignment_map = collections.defaultdict(
        lambda: collections.defaultdict(list))
    for assignment in staff_assignments:
      heat = assignment.heat.get()
      assignment.station = None
      assignment_map[heat.stage.id()][heat.start_time].append(assignment)
    for _, assignments_by_time in assignment_map.iteritems():
      last_time = {}
      for time in sorted(assignments_by_time):
        assignments = assignments_by_time[time]
        this_time = {}
        available = [i + 1 for i in range(len(assignments))]
        for assignment in assignments:
          staff_id = assignment.staff_member.id()
          if staff_id in last_time and last_time[staff_id] in available:
            assignment.station = last_time[staff_id]
            available.remove(last_time[staff_id])
            this_time[staff_id] = last_time[staff_id]
        for assignment in assignments:
          staff_id = assignment.staff_member.id()
          if assignment.station is None:
            next_station = random.choice(available)
            assignment.station = next_station
            available.remove(next_station)
            this_time[staff_id] = next_station
          self.response.write('Assigned %s to station %d for %s' %
                                  (assignment.staff_member.get().name,
                                   assignment.station,
                                   assignment.heat.id()))
          assignment.put()
        last_time = this_time
