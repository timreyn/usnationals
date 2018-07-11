import collections
import datetime
import json

from src.handler import CacheHandler
from src.models import Competitor
from src.models import GroupAssignment
from src.models import StaffAssignment

class GetSchedule(CacheHandler):
  def GetCached(self, person_id):
    hide_old = self.request.get("hide_old") == "1"
    competitor = Competitor.get_by_id(person_id)
    group_assignments = GroupAssignment.query(GroupAssignment.competitor == competitor.key).iter()
    staff_assignments = StaffAssignment.query(StaffAssignment.staff_member == competitor.key).iter()
    schedule_dict = {
        'competitor': competitor.ToDict(),
        'groups' : []
    }
    groups_by_time = collections.defaultdict(list)
    jobs_by_time = collections.defaultdict(list)
    now = datetime.datetime.now() - datetime.timedelta(hours=7)
    for group_assignment in group_assignments:
      group = group_assignment.group.get()
      if hide_old and group.call_time and now - group.call_time > datetime.timedelta(minutes = 30):
        continue
      # HACK HACK HACK
      if hide_old and group.start_time < datetime.datetime(2018, 7, 27):
        continue
      groups_by_time[group.start_time].append(group)
    for staff_assignment in staff_assignments:
      group = staff_assignment.group.get()
      if hide_old and group.call_time and now - group.call_time > datetime.timedelta(minutes = 30):
        continue
      jobs_by_time[group.start_time].append(staff_assignment)
    for time in sorted(groups_by_time.keys() + jobs_by_time.keys()):
      for group in groups_by_time[time]:
        schedule_dict['groups'].append({'competing': group.ToDict()})
      for job in jobs_by_time[time]:
        schedule_dict['groups'].append({'staff': job.ToDict()})
    return json.dumps(schedule_dict), 60
