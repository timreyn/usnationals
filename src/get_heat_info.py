import collections
import json

from src.handler import CacheHandler
from src.models import Competitor
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
    used_stations = []
    for staff_assignment in staff_assignments:
      assignment_dict = staff_assignment.ToDict()
      del assignment_dict['heat']
      heat_info['staff'].append(assignment_dict)
      if staff_assignment.job == 'J':
        used_stations.append(staff_assignment.station)
    num_stations = 0
    if used_stations:
      num_stations = max(used_stations)
    for i in range(num_stations):
      s = i + 1
      if s not in used_stations:
        fake_assignment = StaffAssignment()
        fake_assignment.heat = heat.key
        fake_assignment.staff_member = Competitor(id = '1').key
        fake_assignment.staff_member.get().name = 'N/A'
        fake_assignment.job = 'J'
        fake_assignment.station = s
        heat_info['staff'].append(fake_assignment.ToDict())

    return json.dumps(heat_info), 60
