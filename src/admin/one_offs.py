import datetime
import webapp2

from google.appengine.ext import ndb

from src.models import Competitor
from src.models import Group
from src.models import StaffAssignment

def CloneAssignment(assignment, new_id):
  new_assignment = StaffAssignment(id = new_id)
  new_assignment.group = assignment.group
  if assignment.long_event:
    new_assignment.long_event = assignment.long_event
  new_assignment.staff_member = assignment.staff_member
  new_assignment.job = assignment.job
  if assignment.station:
    new_assignment.station = assignment.station
  if assignment.misc:
    new_assignment.misc = assignment.misc
  return new_assignment
  

class OneOffHandler(webapp2.RequestHandler):
  def get(self, name):
    futures = []
    if name == 'mikael':
      # Give all of Mikael's jobs to Bradley
      mikael = ndb.Key(Competitor, '479')
      bradley = ndb.Key(Competitor, '79')
      for assignment in StaffAssignment.query(StaffAssignment.staff_member == mikael).iter():
        new_assignment = CloneAssignment(assignment, assignment.key.id().replace('479', '79'))
        new_assignment.staff_member = bradley
        futures.append(assignment.key.delete_async())
        futures.append(new_assignment.put_async())
    if name == 'brad':
      # Give Bradley's morning jobs to Felix
      bradley = ndb.Key(Competitor, '79')
      felix = ndb.Key(Competitor, '243')
      bradley_arrives = datetime.datetime(2018, 7, 27, 10, 55, 0)
      for assignment in StaffAssignment.query(StaffAssignment.staff_member == bradley).iter():
        if assignment.start_time > bradley_arrives:
          continue
        new_assignment = CloneAssignment(assignment, assignment.key.id().replace('479', '243').replace('79', '243'))
        new_assignment.staff_member = felix
        futures.append(assignment.key.delete_async())
        futures.append(new_assignment.put_async())
    for future in futures:
      future.get_result()
