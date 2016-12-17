from google.appengine.ext import ndb

from src import common
from src.models.competitor import Competitor
from src.models.event import Event
from src.models.heat import HeatAssignment

class EventRegistration(ndb.Model):
  competitor = ndb.KeyProperty(kind=Competitor)
  event = ndb.KeyProperty(kind=Event)
  heat_assignment = ndb.KeyProperty(kind=HeatAssignment)
  single = ndb.IntegerProperty()
  average = ndb.IntegerProperty()

  @staticmethod
  def Id(competitor_id, event_id):
    return '%s_%s' % (Competitor.Id(competitor_id), Event.Id(event_id))
