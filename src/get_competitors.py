import json

from src.handler import CacheHandler
from src.models import Competitor

class GetCompetitors(CacheHandler):
  def GetCached(self):
    competitor_list = [competitor.ToDict() for competitor in Competitor.query().iter()]
    return json.dumps(competitor_list), 15 * 60
