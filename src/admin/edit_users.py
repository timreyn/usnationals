import datetime
import webapp2

from src import firebase
from src.jinja import JINJA_ENVIRONMENT
from src.models import AdminDevice
from src.models import Competitor

class EditUsers(webapp2.RequestHandler):
  def post(self):
    user_password = self.request.get('password')
    is_admin = self.request.get('is_admin') != ''
    competitor_id = self.request.get('competitor')
    competitor = Competitor.get_by_id(competitor_id)
    if not competitor:
      raise Exception('No matching competitor found!')

    devices = AdminDevice.query(AdminDevice.password == user_password).iter()
    devices_found = False
    for device in devices:
      device.competitor = competitor.key
      if not device.is_authorized and is_admin:
        device.authorized_time = datetime.datetime.now()
        self.NotifyDevice(device, is_admin)
      if device.is_authorized and not is_admin:
        device.deauthorized_time = datetime.datetime.now()
        self.NotifyDevice(device, is_admin)
      device.is_authorized = is_admin
      device.put()
      devices_found = True
    if not devices_found:
      raise Exception('No matching devices found!')
    self.WriteOutput()

  def get(self):
    self.WriteOutput()

  def WriteOutput(self):
    template = JINJA_ENVIRONMENT.get_template('edit_users.html')
    devices = AdminDevice.query().order(-AdminDevice.creation_time).iter()
    competitors = [competitor for competitor in Competitor.query().iter()]
    self.response.write(template.render({
        'devices': devices,
        'competitors': competitors,
        'path' : webapp2.uri_for('edit_users'),
    }))

  def NotifyDevice(self, device, is_admin):
    data = {'isAdmin': '1' if is_admin else '0',
            'deviceId': device.key.id(),
            'competitorName': device.competitor.get().name,
           }
    topic = '/topics/device_' + device.key.id()
    firebase.SendPushNotification(topic, data, 'adminStatus')
