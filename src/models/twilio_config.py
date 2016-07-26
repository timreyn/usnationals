from google.appengine.ext import ndb

class TwilioConfig(ndb.Model):
  phone_number = ndb.StringProperty()
  account_sid = ndb.StringProperty()
  auth_token = ndb.StringProperty()
