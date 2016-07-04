import json

from src.handler import CacheHandler
from src.models import Stage

class GetStages(CacheHandler):
  def GetCached(self):
    stage_list = [stage.ToDict() for stage in Stage.query().iter()]
    return json.dumps(stage_list), 15 * 60
