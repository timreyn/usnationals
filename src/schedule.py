from google.appengine.ext import ndb

import json
import webapp2

from src.models import Competitor
from src.models import HeatAssignment

class GetSchedule(webapp2.RequestHandler):
  def get(self, person_id):
    competitor = Competitor.get_by_id(person_id)
    heat_assignments = HeatAssignment.query(HeatAssignment.competitor == competitor.key).iter()
    schedule_dict = {
        'competitor': competitor.ToDict(),
        'heats' : []
    }
    heats_by_time = {}
    for heat_assignment in heat_assignments:
      heat = heat_assignment.heat.get()
      heats_by_time[heat.start_time] = heat
    for time in sorted(heats_by_time):
      schedule_dict['heats'].append(heats_by_time[time].ToDict())
    self.response.write(json.dumps(schedule_dict))
