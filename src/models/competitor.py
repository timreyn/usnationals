from google.appengine.ext import ndb

class Competitor(ndb.Model):
  name = ndb.StringProperty()
  wca_id = ndb.StringProperty()
  is_staff = ndb.BooleanProperty()
  is_admin = ndb.BooleanProperty()
