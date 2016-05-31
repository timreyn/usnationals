from google.appengine.ext import ndb

from src.models.event import Event

class Round(ndb.Model):
  event = ndb.KeyProperty(kind=Event)
  number = ndb.IntegerProperty()
  cutoff = ndb.IntegerProperty()
  time_limit = ndb.IntegerProperty()
  is_final = ndb.BooleanProperty()
