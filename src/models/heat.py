from google.appengine.ext import ndb

from src.models.competitor import Competitor
from src.models.round import Round
from src.models.stage import Stage

class Heat(ndb.Model):
  round = ndb.KeyProperty(kind=Round)
  stage = ndb.KeyProperty(kind=Stage)
  number = ndb.IntegerProperty()
  start_time = ndb.DateTimeProperty()
  end_time = ndb.DateTimeProperty()

  @staticmethod
  def Id(event_id, round_id, stage, number):
    return '%s_%s_%d' % (Round.Id(event_id, round_id), stage, number)


class HeatAssignment(ndb.Model):
  heat = ndb.KeyProperty(kind=Heat)
  competitor = ndb.KeyProperty(kind=Competitor)

  @staticmethod
  def Id(event_id, round_id, person_id):
    return '%s_%s' % (Round.Id(event_id, round_id), person_id)
