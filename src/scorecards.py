import collections
import json
import webapp2

from src.jinja import JINJA_ENVIRONMENT
from src.models import Event
from src.models import Heat
from src.models import HeatAssignment
from src.models import Round

class GetScorecards(webapp2.RequestHandler):
  def get(self):
    template = JINJA_ENVIRONMENT.get_template('scorecards.tex')
    pages = []
    for round_id in self.request.get('r').split(','):
      r = Round.get_by_id(round_id)
      if not r:
        continue
      if r.event.id() == '333mbf':
        event_name = 'Multiple Blindfolded Attempt %d' % r.number
      elif r.is_final:
        event_name = r.event.get().name + ' Final'
      else:
        event_name = '%s Round %d' % (r.event.get().name, r.number)
      competitors = []
      for heat in Heat.query(Heat.round == r.key).iter():
        if self.request.get('s') and heat.stage.id() not in self.request.get('s'):
          continue
        heat_string = '%s%d' % (heat.stage.id().upper(), heat.number)
        for heat_assignment in HeatAssignment.query(HeatAssignment.heat == heat.key).iter():
          competitor = heat_assignment.competitor.get()
          competitors.append({'name': competitor.name, 'heat': heat_string, 'wcaid': competitor.wca_id, 'id': competitor.key.id()})
          if len(competitors) == 4:
            pages.append({'event': event_name, 'competitors': competitors})
            competitors = []
      if competitors:
        while len(competitors) < 4:
          competitors.append({'name': '', 'heat': '', 'wcaid': '', 'id': ''})
        pages.append({'event': event_name, 'competitors': competitors})
    self.response.write(template.render({'pages': pages}))
