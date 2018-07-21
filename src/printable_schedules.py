import collections
import webapp2

from src.jinja import JINJA_ENVIRONMENT
from src.models import Competitor
from src.models import Event
from src.models import Group
from src.models import GroupAssignment
from src.models import Round

def day(group):
  return group.start_time.strftime('%A')


def sortkey(competitor):
  lastname = competitor.name.split(' ')[-1]
  if competitor.is_staff:
    return '0' + lastname
  return lastname
    

class PrintableSchedulesHandler(webapp2.RequestHandler):
  def get(self):
    competitors = sorted(Competitor.query().fetch(), key=sortkey)
    groups_by_competitor = collections.defaultdict(list)
    groups = Group.query().fetch()
    rounds = Round.query().fetch()
    events = Event.query().fetch()

    for assignment in GroupAssignment.query().iter():
      groups_by_competitor[assignment.competitor.id()].append(assignment.group.get())
    for groups in groups_by_competitor.itervalues():
      groups.sort(key=lambda group: group.start_time)
    competitors = [x for x in competitors if x.key.id() in groups_by_competitor]
    
    template = JINJA_ENVIRONMENT.get_template('printable_schedules.html')

    self.response.write(template.render({
        'competitors': competitors,
        'groups_by_competitor': groups_by_competitor,
        'day': day,
        'len': len,
    }))
