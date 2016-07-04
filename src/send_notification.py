from google.appengine.ext import ndb

import json
import webapp2

from src import firebase
from src.models import AdminDevice
from src.models import Heat
from src.models import HeatAssignment
from src.models import StaffAssignment

class SendNotification(webapp2.RequestHandler):
  def get(self, event_id, round_id, stage_id, heat_number):
    self.post(event_id, round_id, stage_id, heat_number, dry_run=True)

  def post(self, event_id, round_id, stage_id, heat_number, dry_run=False):
    if not dry_run:
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
    if heat.call_time:
      self.response.set_status(403)
      self.resonse.write('Heat has already been called')
      return
    if not dry_run:
      heat.call_time = datetime.now()
      heat.call_device = admin_device.key()
      heat.put()
    event = heat.round.get().event.get()
    stage = heat.stage.get()

    for heat_assignment in HeatAssignment.query(HeatAssignment.heat == heat.key).iter():
      competitor = heat_assignment.competitor.get()
      data = {'heatAssignmentId': heat_assignment.key.id(),
              'eventId': event.key.id(),
              'eventName': event.name,
              'competitorName': competitor.name,
              'competitorId': competitor.key.id(),
              'heatNumber': heat_number,
              'stageName': stage.name}
      topic = '/topics/competitor_' + competitor.key.id()
      if dry_run:
        self.response.write(json.dumps(data))
      else:
        firebase.SendPushNotification(topic, data, 'heatNotification')

    for staff_assignment in StaffAssignment.query(StaffAssignment.heat == heat.key).iter():
      staff_member = staff_assignment.staff_member.get()
      previous_heat = Heat.query(ndb.AND(Heat.end_time == heat.start_time,
                                         Heat.stage == stage.key)).get()
      if previous_heat:
        previous_staff_assignment = StaffAssignment.query(
            ndb.AND(StaffAssignment.heat == previous_heat.key,
                    StaffAssignment.staff_member == staff_member.key)).get()
        if (previous_staff_assignment and
            previous_staff_assignment.job == staff_assignment.job and
            previous_staff_assignment.station == staff_assignment.station):
          continue
      data = {'staffAssignmentId': staff_assignment.key.id(),
              'competitorName': staff_member.name,
              'competitorId': staff_member.key.id(),
              'stageName': stage.name,
              'jobId': staff_assignment.job}
      job_id_to_name = {
          'J': 'Judge',
          'S': 'Scramble',
          'R': 'Run',
          'L': 'Judge',
          'U': 'Scramble',
          'H': 'work at the Help Desk',
          'D': 'do Data Entry',
      }
      data['jobName'] = job_id_to_name[staff_assignment.job]
      topic = '/topics/competitor_' + staff_member.key.id()
      if staff_assignment.job in ('L', 'U'):
        data['eventId'] = staff_assignment.long_event.get().event.id()
      else:
        data['eventId'] = event.key.id()
      if dry_run:
        self.response.write(json.dumps(data))
      else:
        firebase.SendPushNotification(topic, data, 'staffNotification')
