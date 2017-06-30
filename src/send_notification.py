from google.appengine.api import users
from google.appengine.ext import deferred
from google.appengine.ext import ndb

import datetime
import json
import webapp2

from src import firebase
from src import twilio_sms
from src.models import AdminDevice
from src.models import Heat
from src.models import HeatAssignment
from src.models import SMSSubscriber
from src.models import StaffAssignment

class SendNotification(webapp2.RequestHandler):
  def get(self, event_id, round_id, stage_id, heat_number):
    user = users.GetCurrentUser()
    is_admin = self.request.path.startswith('/admin/') and user
    self.post(event_id, round_id, stage_id, heat_number, dry_run=not is_admin)

  def post(self, event_id, round_id, stage_id, heat_number, dry_run=False):
    user = users.GetCurrentUser()
    is_admin = self.request.path.startswith('/admin/') and user
    if not dry_run and not is_admin:
      device_id = self.request.get('device_id')
      admin_device = AdminDevice.get_by_id(device_id)
      if not admin_device or not admin_device.is_authorized:
        self.response.set_status(401)
        self.response.write('Unauthorized')
        return
    if is_admin:
      admin_device = AdminDevice.get_by_id(user.email())
      if not admin_device:
        admin_device = AdminDevice(id = user.email())
        admin_device.authorized_time = datetime.datetime.now()
        # Synthetic admin accounts can't be used to call via the app.
        admin_device.is_authorized = False
        admin_device.put()
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
      self.response.write('Heat has already been called')
      return
    if not dry_run:
      heat.call_time = datetime.datetime.now() - datetime.timedelta(hours=7)
      heat.call_device = admin_device.key
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
        deferred.defer(firebase.SendPushNotification, topic, data, 'heatNotification')
        for subscriber in SMSSubscriber.query(SMSSubscriber.competitor == competitor.key):
          deferred.defer(twilio_sms.SendSMS, heat_assignment, subscriber)

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
        deferred.defer(firebase.SendPushNotification, topic, data, 'staffNotification')
        for subscriber in SMSSubscriber.query(SMSSubscriber.competitor == staff_member.key):
          deferred.defer(twilio_sms.SendStaffSMS, staff_assignment, subscriber)
    self.response.set_status(200)
