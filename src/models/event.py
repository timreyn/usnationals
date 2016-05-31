from google.appengine.ext import ndb

class Event(ndb.Model):
  name = ndb.StringProperty()
  priority = ndb.IntegerProperty()
  is_real = ndb.BooleanProperty()

  @staticmethod
  def Get(event_id):
    events = Event.query(Event.id == event_id).iter()
    if not events:
      return None
    return events[0]
