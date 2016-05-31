from google.appengine.ext import ndb

class Stage(ndb.Model):
  name = ndb.StringProperty()
  color_hex = ndb.StringProperty()

  def ToDict(self):
    return {
        'id' : self.key.id(),
        'name' : self.name,
        'color_hex' : self.color_hex,
    }
