import collections
import datetime
import json

from src.common import TZ
from src.handler import CacheHandler
from src.models import AdminDevice
from src.models import Group

class GetStageSchedule(CacheHandler):
  def GetCached(self, stages='all'):
    device_id = self.request.get('device_id')
    if device_id:
      device = AdminDevice.get_by_id(device_id)
      is_admin = device and device.is_authorized
    else:
      is_admin = False
    output_dict = {
        'is_admin': is_admin,
        'groups': [],
    }
    groups = Group.query().iter()
    groups_by_time = collections.defaultdict(list)
    now = TZ.localize(datetime.datetime.utcnow())
    for group in groups:
      if group.call_time and now - group.call_time > datetime.timedelta(minutes = 30):
        continue
      if stages == 'all' or group.stage.id() in stages:
        groups_by_time[group.start_time].append(group)
    for time in sorted(groups_by_time):
      for group in groups_by_time[time]:
        if group.round.get().event.get().is_real:
          output_dict['groups'].append(group.ToDict())
    return json.dumps(output_dict), 5 * 60
