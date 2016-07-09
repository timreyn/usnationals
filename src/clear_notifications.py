import webapp2

from src.models import Heat

class ClearNotifications(webapp2.RequestHandler):
  def get(self):
    for heat in Heat.query().iter():
      if heat.call_time:
        heat.call_time = None
        heat.call_device = None
        heat.put()
        self.response.write('Cleared notification for ' + heat.key.id() + '\n')
