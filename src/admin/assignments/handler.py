from google.appengine.ext import deferred

from src.admin.assignments.assign_groups import AssignGroups
from src.models import ActiveAssignment
from src.models import Round

import datetime
import hashlib
import webapp2

class AssignmentsHandler(webapp2.RequestHandler):
  def get(self):
    rounds = [Round.get_by_id(rid) for rid in self.request.get('r').split(',')]
    request_id = hashlib.sha1(datetime.datetime.now().isoformat()).hexdigest()[0:10]
#    AssignGroups(rounds, request_id)
    deferred.defer(AssignGroups, rounds, request_id)
    active_assignment = ActiveAssignment.get_by_id('1') or ActiveAssignment(id='1')
    active_assignment.request_id = request_id
    active_assignment.put()
    self.redirect(webapp2.uri_for('assign_groups_debug', request_id=request_id))
