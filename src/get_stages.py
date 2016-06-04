import json
import webapp2

from src.models import Stage

class GetStages(webapp2.RequestHandler):
  def get(self):
    stage_list = [stage.ToDict() for stage in Stage.query().iter()]
    self.response.write(json.dumps(stage_list))
