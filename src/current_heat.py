import datetime
import json
import pytz
import webapp2

from src.models import Heat
from src.models import Stage

class CurrentHeat(webapp2.RequestHandler):
  def get(self, stage_id):
    stage = Stage.get_by_id(stage_id)
    if not stage:
      return
    current_heat = None
    next_heat = None
    output = {}
    now = datetime.datetime.now() - datetime.timedelta(hours=7) # hack!
    for heat in Heat.query(Heat.stage == stage.key).iter():
      if not heat.round.get().event.get().is_real:
        continue
      if heat.key.id() == '333oh_1_o_0':
        continue
      if heat.call_time:
        if not current_heat or heat.call_time > current_heat.call_time:
          current_heat = heat
      else:
        if not next_heat or heat.start_time < next_heat.start_time:
          next_heat = heat
    if current_heat:
      output['current_heat'] = current_heat.ToDict()
    if next_heat:
      output['next_heat'] = {'heat': next_heat.ToDict()}
      if current_heat and current_heat.end_time >= next_heat.start_time:
        estimated_call_time = next_heat.start_time + (current_heat.call_time - current_heat.start_time)
      else:
        estimated_call_time = next_heat.start_time
      expected_seconds = max(0, int((estimated_call_time - now).total_seconds()))
      low_end = expected_seconds / (60 * 5) * 5
      high_end = low_end + 5
      output['next_heat']['estimate'] = '%d &mdash; %d minutes' % (low_end, high_end)
    self.response.headers.add_header("Access-Control-Allow-Origin", "*")
    self.response.headers['Content-Type'] = 'application/json'
    self.response.write(json.dumps(output))
