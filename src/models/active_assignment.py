from google.appengine.ext import ndb

class ActiveAssignment(ndb.Model):
  request_id = ndb.StringProperty()
