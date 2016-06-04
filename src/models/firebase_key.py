from google.appengine.ext import ndb

class FirebaseKey(ndb.Model):
  f_key = ndb.StringProperty()
