import collections
import datetime
import json

from src.handler import CacheHandler
from src.models import Competitor
from src.models import HeatAssignment
from src.models import StaffAssignment

class GetSchedule(CacheHandler):
  def GetCached(self, person_id):
    hide_old = self.request.get("hide_old") == "1"
    competitor = Competitor.get_by_id(person_id)
    heat_assignments = HeatAssignment.query(HeatAssignment.competitor == competitor.key).iter()
    staff_assignments = StaffAssignment.query(StaffAssignment.staff_member == competitor.key).iter()
    schedule_dict = {
        'competitor': competitor.ToDict(),
        'heats' : []
    }
    heats_by_time = collections.defaultdict(list)
    jobs_by_time = collections.defaultdict(list)
    now = datetime.datetime.now() - datetime.timedelta(hours=7)
    for heat_assignment in heat_assignments:
      heat = heat_assignment.heat.get()
      if hide_old and heat.call_time and now - heat.call_time > datetime.timedelta(minutes = 30):
        continue
      # HACK HACK HACK
      if hide_old and heat.key.id() == '333oh_1_o_0':
        continue
      heats_by_time[heat.start_time].append(heat)
    for staff_assignment in staff_assignments:
      heat = staff_assignment.heat.get()
      if hide_old and heat.call_time and now - heat.call_time > datetime.timedelta(minutes = 30):
        continue
      jobs_by_time[heat.start_time].append(staff_assignment)
    for time in sorted(heats_by_time.keys() + jobs_by_time.keys()):
      for heat in heats_by_time[time]:
        schedule_dict['heats'].append({'competing': heat.ToDict()})
      for job in jobs_by_time[time]:
        schedule_dict['heats'].append({'staff': job.ToDict()})
    return json.dumps(schedule_dict), 60
