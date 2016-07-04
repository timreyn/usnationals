import collections
import json
import webapp2

from src.models import Heat
from src.models import HeatAssignment
from src.models import StaffAssignment

class GetHeatInfo(webapp2.RequestHandler):
  def get(self, event_id, round_id, stage, number):
    heat = Heat.get_by_id(Heat.Id(event_id, int(round_id), stage, int(number)))
    if not heat:
      return
    heat_info = {
        'heat': heat.ToDict(),
        'competitors': [],
        'staff': [],
    }
    heat_assignments = HeatAssignment.query(HeatAssignment.heat == heat.key).iter()
    heat_assignments_by_name = {}
    for heat_assignment in heat_assignments:
      competitor = heat_assignment.competitor.get()
      heat_assignments_by_name[competitor.name] = competitor
    for name in sorted(heat_assignments_by_name):
      heat_info['competitors'].append(heat_assignments_by_name[name].ToDict())

    staff_assignments = StaffAssignment.query(StaffAssignment.heat == heat.key).iter()
    for staff_assignment in staff_assignments:
      heat_info['staff'].append(staff_assignment.ToDict())

    self.response.write(json.dumps(heat_info))
