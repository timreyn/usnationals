import collections
import json

from src.handler import CacheHandler
from src.models import Competitor
from src.models import Group
from src.models import GroupAssignment
from src.models import StaffAssignment

class GetGroupInfo(CacheHandler):
  def GetCached(self, event_id, round_id, stage, number):
    group = Group.get_by_id(Group.Id(event_id, int(round_id), stage, number))
    if not group:
      return '', 60
    group_info = {
        'group': group.ToDict(),
        'competitors': [],
        'staff': [],
    }
    group_assignments = GroupAssignment.query(GroupAssignment.group == group.key).iter()
    group_assignments_by_name = {}
    for group_assignment in group_assignments:
      competitor = group_assignment.competitor.get()
      group_assignments_by_name[competitor.name] = competitor
    for name in sorted(group_assignments_by_name):
      group_info['competitors'].append(group_assignments_by_name[name].ToDict())

    staff_assignments = StaffAssignment.query(StaffAssignment.group == group.key).iter()
    used_stations = []
    for staff_assignment in staff_assignments:
      assignment_dict = staff_assignment.ToDict()
      del assignment_dict['group']
      group_info['staff'].append(assignment_dict)
      if staff_assignment.job == 'J':
        used_stations.append(staff_assignment.station)
    num_stations = 0
    if used_stations:
      num_stations = max(used_stations)
    for i in range(num_stations):
      s = i + 1
      if s not in used_stations:
        fake_assignment = StaffAssignment()
        fake_assignment.group = group.key
        fake_assignment.staff_member = Competitor(id = '1').key
        fake_assignment.staff_member.get().name = 'N/A'
        fake_assignment.job = 'J'
        fake_assignment.station = s
        group_info['staff'].append(fake_assignment.ToDict())

    return json.dumps(group_info), 60
