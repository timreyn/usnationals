from google.appengine.ext import ndb

from src.models.event import Event

class Round(ndb.Model):
  event = ndb.KeyProperty(kind=Event)
  number = ndb.IntegerProperty()
  cutoff = ndb.IntegerProperty()
  time_limit = ndb.IntegerProperty()
  is_final = ndb.BooleanProperty()

  @staticmethod
  def Id(event_id, round_num):
    return '%s_%d' % (event_id, round_num)

  def ToDict(self):
    return {
        'id' : self.key.id(),
        'event' : self.event.get().ToDict(),
        'number' : self.number,
        'cutoff' : self.cutoff,
        'time_limit' : self.time_limit,
        'is_final' : self.is_final,
    }
