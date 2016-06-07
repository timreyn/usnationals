import collections
import json
import webapp2

from src.models import Competitor
from src.models import HeatAssignment
from src.models import StaffAssignment

class GetSchedule(webapp2.RequestHandler):
  def get(self, person_id):
    competitor = Competitor.get_by_id(person_id)
    heat_assignments = HeatAssignment.query(HeatAssignment.competitor == competitor.key).iter()
    staff_assignments = StaffAssignment.query(StaffAssignment.staff_member == competitor.key).iter()
    schedule_dict = {
        'competitor': competitor.ToDict(),
        'heats' : []
    }
    heats_by_time = collections.defaultdict(list)
    jobs_by_time = collections.defaultdict(list)
    for heat_assignment in heat_assignments:
      heat = heat_assignment.heat.get()
      heats_by_time[heat.start_time].append(heat)
    for staff_assignment in staff_assignments:
      heat = staff_assignment.heat.get()
      jobs_by_time[heat.start_time].append(staff_assignment)
    for time in sorted(heats_by_time.keys() + jobs_by_time.keys()):
      for heat in heats_by_time[time]:
        schedule_dict['heats'].append({'competing': heat.ToDict()})
      for job in jobs_by_time[time]:
        schedule_dict['heats'].append({'staff': job.ToDict()})
    self.response.write(json.dumps(schedule_dict))
