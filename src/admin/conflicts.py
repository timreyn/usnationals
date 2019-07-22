from google.appengine.api import users

import collections
import webapp2

from src.common import TZ
from src.jinja import JINJA_ENVIRONMENT
from src.models import Competitor
from src.models import Group
from src.models import GroupAssignment
from src.models import Round
from src.models import Stage

def format_time(time):
  return TZ.localize(time).strftime('%A %H:%M')

class Conflict(object):
  def __init__(self, competitor, group1, group2):
    self.competitor = competitor
    self.group1 = group1
    self.group2 = group2
    self.timediff = self.group2.start_time - self.group1.end_time

class ConflictsHandler(webapp2.RequestHandler):
  def get(self):
    groups = {g.key.id() : g for g in Group.query().iter()}
    rounds = {r.key.id() : r for r in Round.query().iter()}
    competitors = {c.key.id() : c for c in Competitor.query().iter()}

    groups_by_person = collections.defaultdict(list)
    conflicts = []
    for assignment in GroupAssignment.query().iter():
      groups_by_person[assignment.competitor.id()].append(assignment.group.get())
    for competitor_id, groups in groups_by_person.iteritems():
      groups.sort(key=lambda g: g.start_time, reverse=True)
      for g1, g2 in zip(groups[1:], groups[:-1]):
        conflicts.append(Conflict(competitors[competitor_id], g1, g2))
    conflicts.sort(key=lambda c: c.timediff)

    template = JINJA_ENVIRONMENT.get_template('conflicts.html')
    self.response.write(template.render({
        'conflicts': conflicts,
        'format_time': format_time,
    }))
