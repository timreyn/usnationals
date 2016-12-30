from src.models import DebugInfo

import webapp2

class AssignmentsDebugHandler(webapp2.RequestHandler):
  def get(self, request_id):
    debug_info = DebugInfo.get_by_id(request_id)
    if debug_info:
      self.response.write(debug_info.info)
