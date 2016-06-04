from google.appengine.ext import ndb

class FirebaseKey(ndb.Model):
  key = ndb.StringProperty()
