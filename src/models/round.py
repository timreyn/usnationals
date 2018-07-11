from google.appengine.ext import ndb

from src.models.event import Event

class Round(ndb.Model):
  event = ndb.KeyProperty(kind=Event)
  number = ndb.IntegerProperty()
  is_final = ndb.BooleanProperty()
  group_length = ndb.IntegerProperty()
  num_competitors = ndb.IntegerProperty()

  @staticmethod
  def Id(event_id, round_num):
    return '%s_%d' % (event_id, round_num)

  def ToDict(self):
    output = {
        'id' : self.key.id(),
        'event' : self.event.get().ToDict(),
        'number' : self.number,
        'is_final' : self.is_final,
    }
    if self.number > 1:
      output['num_competitors'] = self.num_competitors
    return output
