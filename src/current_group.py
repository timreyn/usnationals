import datetime
import json
import pytz
import webapp2

from src.models import Group
from src.models import Stage

class CurrentGroup(webapp2.RequestHandler):
  def get(self, stage_id):
    stage = Stage.get_by_id(stage_id)
    if not stage:
      return
    current_group = None
    next_group = None
    output = {}
    now = datetime.datetime.now() - datetime.timedelta(hours=6) # hack! time zones are hard
    for group in Group.query(Group.stage == stage.key).iter():
      if not group.round.get().event.get().is_real:
        continue
      if group.start_time < datetime.datetime(2018, 7, 27):
        continue
      if group.call_time:
        if not current_group or group.call_time > current_group.call_time:
          current_group = group
      else:
        if not next_group or group.start_time < next_group.start_time:
          next_group = group
    if current_group:
      output['current_group'] = current_group.ToDict()
    if next_group:
      output['next_group'] = {'group': next_group.ToDict()}
      if current_group and current_group.end_time >= next_group.start_time:
        estimated_call_time = next_group.start_time + (current_group.call_time - current_group.start_time) + datetime.timedelta(hours=3)
      else:
        estimated_call_time = next_group.start_time
      expected_seconds = max(0, int((estimated_call_time - now).total_seconds()))
      low_end = expected_seconds / (60 * 5) * 5
      high_end = low_end + 5
      output['next_group']['estimate'] = '%d &mdash; %d minutes' % (low_end, high_end)
    self.response.headers.add_header("Access-Control-Allow-Origin", "*")
    self.response.headers['Content-Type'] = 'application/json'
    self.response.write(json.dumps(output))
