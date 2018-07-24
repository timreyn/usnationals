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


def TransferAssignments(old_staff_id, new_staff_id, futures, start=None, end=None):
  old_staff = ndb.Key(Competitor, old_staff_id)
  new_staff = ndb.Key(Competitor, new_staff_id)
  for assignment in StaffAssignment.query(StaffAssignment.staff_member == old_staff).iter():
    if end and assignment.group.get().start_time > end:
      continue
    if start and assignment.group.get().start_time < start:
      continue
    new_assignment = CloneAssignment(assignment, assignment.key.id().replace(old_staff_id, new_staff_id))
    new_assignment.staff_member = new_staff
    futures.append(assignment.key.delete_async())
    futures.append(new_assignment.put_async())
  

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
        if assignment.group.get().start_time > bradley_arrives:
          continue
        new_assignment = CloneAssignment(assignment, assignment.key.id().replace('479', '243').replace('79', '243'))
        new_assignment.staff_member = felix
        futures.append(assignment.key.delete_async())
        futures.append(new_assignment.put_async())
    if name == 'cari':
      # There are two Cari Goslows in the registration system.  One is right, one is wrong.
      TransferAssignments('710', '115', futures)
      wrong_cari = ndb.Key(Competitor, '710')
      right_cari = ndb.Key(Competitor, '115')
      futures.append(wrong_cari.delete_async())
      right_cari = right_cari.get()
      right_cari.is_staff = True
      right_cari.put()
    if name == 'clarke':
      # Clarke will be late.  Give his early jobs to lachance.
      TransferAssignments('152', '298', futures,
                          end=datetime.datetime(2018, 7, 27, 15, 30))
    if name == 'dalton':
      # Dalton is missing Saturday.  Give his jobs to felix.
      TransferAssignments('167', '243', futures,
                          start=datetime.datetime(2018, 7, 28, 0, 0),
                          end=datetime.datetime(2018, 7, 28, 23, 59))
    if name == 'dalton_ii':
      # And undo part of that, since I transferred too much.
      TransferAssignments('243', '167', futures,
                          end=datetime.datetime(2018, 7, 28, 0, 0))
    for future in futures:
      future.get_result()
