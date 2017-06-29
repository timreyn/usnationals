import webapp2

from src.models import Competitor
from src.models import StaffAssignment

class OneOffHandler(webapp2.RequestHandler):
  def get(self, name):
    futures = []
    if name == 'garrett':
      # Give all of Nathan Dwyer's judging jobs to Garrett Webster.
      garrett = Competitor.get_by_id('277')
      nathan = Competitor.get_by_id('533')
      for assignment in StaffAssignment.query(StaffAssignment.staff_member == nathan.key).iter():
        assignment.staff_member = garrett.key
        futures.append(assignment.put_async())
    for future in futures:
      future.get_result()
