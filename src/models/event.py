from google.appengine.ext import ndb

class Event(ndb.Model):
  name = ndb.StringProperty()
  priority = ndb.IntegerProperty()
  is_real = ndb.BooleanProperty()

  def ToDict(self):
    return {
        'id' : self.key.id(),
        'name' : self.name,
        'priority' : self.priority,
        'is_real' : self.is_real,
    }
