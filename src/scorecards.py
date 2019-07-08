import collections
import json
import webapp2

from src.jinja import JINJA_ENVIRONMENT
from src.models import Event
from src.models import EventRegistration
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
    per_group = int(self.request.get('per') or 4)
    overall = int(self.request.get('overall') or 16)
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
      times_by_competitor = {}
      for event_registration in EventRegistration.query(EventRegistration.event == r.event).iter():
        times_by_competitor[event_registration.competitor.id()] = event_registration.single
      top_times = sorted(times_by_competitor.values())[:overall]
      for group in Group.query(Group.round == r.key).iter():
        if self.request.get('s') and group.stage.id() not in self.request.get('s'):
          continue
        if staff_status == STAFF_ONLY and not group.staff:
          continue
        if staff_status == NON_STAFF_ONLY and group.staff:
          continue
        group_string = '%s%s%d' % (group.stage.id().upper(), 'S' if group.staff else '', group.number)
        competitors_in_group = []
        times_in_group = []
        for group_assignment in GroupAssignment.query(GroupAssignment.group == group.key).iter():
          competitor = group_assignment.competitor.get()
          competitors_in_group.append({'name': competitor.name, 'group': group_string, 'wcaid': competitor.wca_id, 'id': competitor.key.id()})
          times_in_group.append(times_by_competitor[competitor.key.id()])
        top_times_in_group = sorted(times_in_group)[:per_group]

        competitors_on_page = []
        for competitor in competitors_in_group:
          competitor['is_top'] = times_by_competitor[competitor['id']] in top_times + top_times_in_group
          competitors_on_page.append(competitor)
          if len(competitors_on_page) == 4:
            pages.append({'event': event_name, 'competitors': competitors_on_page})
            competitors_on_page = []
        if competitors_on_page:
          while len(competitors_on_page) < 4:
            competitors_on_page.append({'name': '', 'group': '', 'wcaid': '', 'id': '', 'is_top': False})
          pages.append({'event': event_name, 'competitors': competitors_on_page})
    self.response.write(template.render({'pages': pages}))
