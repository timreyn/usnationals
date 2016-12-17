from google.appengine.ext import ndb

class Competitor(ndb.Model):
  name = ndb.StringProperty()
  wca_id = ndb.StringProperty()
  is_staff = ndb.BooleanProperty()
  is_admin = ndb.BooleanProperty()
  # date_of_birth should not be included in ToDict, since this would make it
  # public.
  date_of_birth = ndb.DateTimeProperty()

  def ToDict(self):
    return {
        'id' : self.key.id(),
        'name' : self.name,
        'wca_id' : self.wca_id,
        'is_staff' : self.is_staff,
        'is_admin' : self.is_admin,
    }
