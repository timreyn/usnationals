from google.appengine.ext import ndb

from src.models.competitor import Competitor

class AdminDevice(ndb.Model):
  password = ndb.StringProperty()
  competitor = ndb.KeyProperty(kind=Competitor)
  is_authorized = ndb.BooleanProperty()
  creation_time = ndb.DateTimeProperty()
  authorized_time = ndb.DateTimeProperty()
  deauthorized_time = ndb.DateTimeProperty()
