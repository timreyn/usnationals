import webapp2

from src import firebase
from src.models import Heat
from src.models import HeatAssignment

class SendNotification(webapp2.RequestHandler):
  def post(self, event_id, round_id, stage_id, heat_number):
    device_id = self.request.get('device_id')
    admin_device = AdminDevice.get_by_id(device_id)
    if not admin_device or not admin_device.is_authorized:
      self.response.set_status(401)
      self.response.write('Unauthorized')
      return
    round_id = int(round_id)
    heat_number = int(heat_number)
    heat_id = Heat.Id(event_id, round_id, stage_id, heat_number)
    heat = Heat.get_by_id(heat_id)
    if not heat:
      self.response.set_status(400)
      self.response.write('No heat found for ' + heat_id)
      return
    event = heat.round.get().event.get()
    stage = heat.stage.get()

    # TODO: record the time, and don't send notifications too frequently
    for heat_assignment in HeatAssignment.query(HeatAssignment.heat == heat.key).iter():
      competitor = heat_assignment.competitor.get()
      data = {"heatAssignmentId": heat_assignment.key.id(),
              "eventId": event.key.id(),
              "eventName": event.name,
              "competitorName": competitor.name,
              "competitorId": competitor.key.id(),
              "heatNumber": heat_number,
              "stageName": stage.name}
      topic = "/topics/competitor_" + competitor.key.id()
      firebase.SendPushNotification(topic, data, "heatNotification")
