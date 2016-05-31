from google.appengine.ext import ndb

class Competitor(ndb.Model):
  id = ndb.StringProperty()
  name = ndb.StringProperty()
  wca_id = ndb.StringProperty()
