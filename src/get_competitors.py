import json
import webapp2

from src.models import Competitor

class GetCompetitors(webapp2.RequestHandler):
  def get(self):
    competitor_list = [competitor.ToDict() for competitor in Competitor.query().iter()]
    self.response.write(json.dumps(competitor_list))
