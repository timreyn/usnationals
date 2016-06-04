import httplib
import json
import webapp2

from src.models import FirebaseKey
from src.models import Heat
from src.models import HeatAssignment

class SendNotification(webapp2.RequestHandler):
  # TODO: change this to post
  def get(self, event_id, round_id, stage_id, heat_number):
    heat_id = Heat.Id(event_id, round_id, stage_id, heat_number)
    heat = Heat.get_by_id(heat_id)
    if not heat:
      self.response.set_status(400)
      self.response.write('No heat found for ' + heat_id)
      return
    firebase_key = FirebaseKey.get_by_id("1")
    if not firebase_key:
      self.response.set_status(500)
      self.response.write('Failed to find Firebase credentials!')
      return
    event = heat.round.get().event.get()
    stage = heat.stage.get()

    # TODO: record the time, and don't send notifications too frequently
    for heat_assignment in HeatAssignment.query(HeatAssignment.heat == heat.key).iter():
      self.SendNotification(heat_assignment, heat_number, event, stage, firebase_key)
    
  def SendNotification(self, heat_assignment, heat_number, event, stage, firebase_key):
    competitor = heat_assignment.competitor.get()
    headers = {'Content-Type': 'application/json',
               'Authorization': 'key=' + firebase_key.f_key}
    conn = httplib.HTTPConnection("https://fcm.googleapis.com/fcm/send")
    data = {"type": "heatNotification",
            "heatAssignmentId": heat_assignment.key.id(),
            "eventId": event.key.id(),
            "eventName": event.name,
            "competitorName": competitor.name,
            "competitorId": competitor.key.id(),
            "heatNumber": heat_number,
            "stageName": stage.name}
    request = {"to": "competitor_" + competitor.key.id(),
               "data": data}
    conn.request("POST", json.dumps(request), {}, headers)
    
    print response.status, response.reason, response.read()
