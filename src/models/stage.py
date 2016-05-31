from google.appengine.ext import ndb

class Stage(ndb.Model):
  id = ndb.StringProperty()
  name = ndb.StringProperty()
  color_hex = ndb.StringProperty()
