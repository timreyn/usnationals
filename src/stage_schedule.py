import collections
import datetime
import json

from src.handler import CacheHandler
from src.models import AdminDevice
from src.models import Heat

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
        'heats': [],
    }
    heats = Heat.query().iter()
    heats_by_time = collections.defaultdict(list)
    now = datetime.datetime.now() - datetime.timedelta(hours = 7)
    for heat in heats:
      if heat.call_time and now - heat.call_time > datetime.timedelta(minutes = 30):
        continue
      # HACK HACK HACK
      if heat.start_time < datetime.datetime(2017, 7, 7):
        continue
      if stages == 'all' or heat.stage.id() in stages:
        heats_by_time[heat.start_time].append(heat)
    for time in sorted(heats_by_time):
      for heat in heats_by_time[time]:
        if heat.round.get().event.get().is_real:
          output_dict['heats'].append(heat.ToDict())
    return json.dumps(output_dict), 5 * 60
