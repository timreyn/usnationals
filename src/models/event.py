from google.appengine.ext import ndb

class Event(ndb.Model):
  name = ndb.StringProperty()
  priority = ndb.IntegerProperty()
  is_real = ndb.BooleanProperty()
