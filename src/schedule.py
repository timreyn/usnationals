from google.appengine.ext import ndb

import webapp2

from src.models import Competitor

class GetSchedule(webapp2.RequestHandler):
  def get(self, person_id):
    competitor_query = Competitor.query(Competitor.reg_id == int(person_id)).fetch(1)
    if not competitor_query:
      self.response.write('No competitor found')
      return
    competitor = competitor_query[0]
    self.response.write(competitor.name)
