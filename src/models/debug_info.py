from google.appengine.ext import ndb

class DebugInfo(ndb.Model):
  info = ndb.StringProperty()
