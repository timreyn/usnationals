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

class HeatAssignment(ndb.Model):
  heat = ndb.KeyProperty(kind=Heat)
  competitor = ndb.KeyProperty(kind=Competitor)
