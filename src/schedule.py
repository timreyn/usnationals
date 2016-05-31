from google.appengine.ext import ndb

import webapp2

from src.models import Competitor

class GetSchedule(webapp2.RequestHandler):
  def get(self, person_id):
    competitor = Competitor.get_by_id(person_id)
    self.response.write(competitor.name)
