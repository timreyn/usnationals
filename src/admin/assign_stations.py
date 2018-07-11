import collections
import random
import webapp2

from src.models import StaffAssignment

class AssignStations(webapp2.RequestHandler):
  def get(self, stage_id):
    staff_assignments = StaffAssignment.query(StaffAssignment.job == "J").iter()
    assignment_map = collections.defaultdict(list)
    stage_substr = '_%s_' % stage_id
    futures = []
    for assignment in staff_assignments:
      if stage_substr not in assignment.key.id():
        continue
      group = assignment.group.get()
      assignment.station = None
      assignment_map[group.start_time].append(assignment)
    last_time = {}
    for time in sorted(assignment_map):
      assignments = assignment_map[time]
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
                                 assignment.group.id()))
        futures.append(assignment.put_async())
      last_time = this_time
    for future in futures:
      future.get_result()
