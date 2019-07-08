import datetime
import webapp2

from src.models import AdminDevice

class RegisterDevice(webapp2.RequestHandler):
  def post(self):
    device_id = self.request.get('id')
    device_password = self.request.get('password')
    device = AdminDevice.get_by_id(device_id) 
    if self.request.get('unregister') == '1':
      if device:
        device.deauthorized_time = datetime.datetime.utcnow()
        device.is_authorized = False
        device.put()
      return
    if not device:
      device = AdminDevice(id = device_id)
    device.is_authorized = False
    device.creation_time = datetime.datetime.utcnow()
    device.password = device_password
    device.put()
