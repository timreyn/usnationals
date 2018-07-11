import webapp2

from src.models import Group

class ClearNotifications(webapp2.RequestHandler):
  def get(self):
    futures = []
    for group in Group.query().iter():
      if group.call_time:
        group.call_time = None
        group.call_device = None
        futures.append(group.put_async())
        self.response.write('Cleared notification for ' + group.key.id() + '\n')
    for future in futures:
      future.get_result()
