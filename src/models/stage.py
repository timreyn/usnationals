from google.appengine.ext import ndb

class Stage(ndb.Model):
  name = ndb.StringProperty()
  color_hex = ndb.StringProperty()
