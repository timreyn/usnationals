import collections
import json
import webapp2

from src.jinja import JINJA_ENVIRONMENT
from src.models import Event
from src.models import Group
from src.models import GroupAssignment
from src.models import Round

DEFAULT = 0
STAFF_ONLY = 1
NON_STAFF_ONLY = 2


class GetScorecards(webapp2.RequestHandler):
  def get(self):
    template = JINJA_ENVIRONMENT.get_template('scorecards.tex')
    pages = []
    staff_status = DEFAULT
    if self.request.get('staff') == 'yes':
      staff_status = STAFF_ONLY
    elif self.request.get('staff') == 'no':
      staff_status = NON_STAFF_ONLY
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
      for group in Group.query(Group.round == r.key).iter():
        if self.request.get('s') and group.stage.id() not in self.request.get('s'):
          continue
        if staff_status == STAFF_ONLY and group.number != 0:
          continue
        if staff_status == NON_STAFF_ONLY and group.number == 0:
          continue
        group_string = '%s%d' % (group.stage.id().upper(), group.number)
        for group_assignment in GroupAssignment.query(GroupAssignment.group == group.key).iter():
          competitor = group_assignment.competitor.get()
          competitors.append({'name': competitor.name, 'group': group_string, 'wcaid': competitor.wca_id, 'id': competitor.key.id()})
          if len(competitors) == 4:
            pages.append({'event': event_name, 'competitors': competitors})
            competitors = []
        if competitors:
          while len(competitors) < 4:
            competitors.append({'name': '', 'group': '', 'wcaid': '', 'id': ''})
          pages.append({'event': event_name, 'competitors': competitors})
    self.response.write(template.render({'pages': pages}))
