import collections
import json

from src.handler import CacheHandler
from src.models import Heat
from src.models import HeatAssignment
from src.models import StaffAssignment

class GetHeatInfo(CacheHandler):
  def GetCached(self, event_id, round_id, stage, number):
    heat = Heat.get_by_id(Heat.Id(event_id, int(round_id), stage, int(number)))
    if not heat:
      return '', 60
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
      assignment_dict = staff_assignment.ToDict()
      del assignment_dict['heat']
      heat_info['staff'].append(assignment_dict)

    return json.dumps(heat_info), 60
