import webapp2

from src import firebase
from src.models import FirebaseKey

class SetFirebaseKey(webapp2.RequestHandler):
  # This should really be a POST...but it's easier this way.
  # Or really this should just be part of add_data.py, like everything else...
  def get(self, key):
    firebase_key = FirebaseKey.get_by_id('1') or FirebaseKey(id = '1')
    firebase_key.f_key = key
    firebase_key.put()
    self.response.write('Success!')
