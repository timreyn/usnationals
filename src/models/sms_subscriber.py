from google.appengine.ext import ndb

from src.models.competitor import Competitor

class SMSSubscriber(ndb.Model):
  competitor = ndb.KeyProperty(kind=Competitor)
  phone_number = ndb.StringProperty()
