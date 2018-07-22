import webapp2

class CubecompsRedirect(webapp2.RequestHandler):
  def get(self, person_id=''):
    # TODO: change this to the cubecomps path for the competition.
    self.redirect('https://m.cubecomps.com/')
