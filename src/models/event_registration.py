from google.appengine.ext import ndb

from src import common
from src.models.competitor import Competitor
from src.models.event import Event
from src.models.group import GroupAssignment

class EventRegistration(ndb.Model):
  competitor = ndb.KeyProperty(kind=Competitor)
  event = ndb.KeyProperty(kind=Event)
  group_assignment = ndb.KeyProperty(kind=GroupAssignment)
  single = ndb.IntegerProperty()
  average = ndb.IntegerProperty()
  projected_rounds = ndb.IntegerProperty()
  non_staff_rank = ndb.IntegerProperty()

  @staticmethod
  def Id(competitor_id, event_id):
    return '%s_%s' % (competitor_id, event_id)
