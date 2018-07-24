import webapp2

class CubecompsRedirect(webapp2.RequestHandler):
  def get(self, person_id=''):
    if person_id:
      self.redirect('http://m.cubecomps.com/competitions/3381/competitors/' + person_id)
    else:
      self.redirect('http://m.cubecomps.com/competitions/3381')
