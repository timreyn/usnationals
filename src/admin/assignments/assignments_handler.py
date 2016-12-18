from google.appengine.ext import deferred

from src.admin.assignments.assign_heats import AssignHeats
from src.models import Heat

import datetime
import hashlib
import webapp2

class AssignmentsHandler(webapp2.RequestHandler):
  def get(self):
    rounds = [Round.get_by_id(rid) for rid in self.request.get('r').split(',')]
    request_id = hashlib.sha1(datetime.datetime.now().isoformat()).hexdigest()[0:10]
    deferred.defer(AssignHeats, rounds, request_id)
