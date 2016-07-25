import collections
import webapp2

from src.jinja import JINJA_ENVIRONMENT
from src.models import StaffAssignment
from src.models import Stage

class JobSchedule(webapp2.RequestHandler):
  def get(self, stage_id, job, station=None):
    stage = Stage.get_by_id(stage_id)
    if not stage:
      return 'Couldn\'t find stage ' + stage_id
    assignments_query = StaffAssignment.query(StaffAssignment.job == job)
    if station:
      station = int(station)
      assignments_query = assignments_query.filter(StaffAssignment.station == station)
    job_name = {
        'J': 'Judging',
        'S': 'Scrambling',
        'R': 'Running',
    }[job]
    title = '%s Stage %s' % (stage.name, job_name)
    if station:
      title += ' %d' % station
    jobs_by_time = collections.defaultdict(list)
    output = {
        'title': title,
        'all_assignments': [],
        'format': '%I:%M %p',
    }
    for staff_assignment in assignments_query.iter():
      heat = staff_assignment.heat.get()
      if heat.stage.id() != stage_id:
        continue
      jobs_by_time[heat.start_time].append(staff_assignment)
    active_staff = collections.defaultdict(list)
    for time in sorted(jobs_by_time.keys()):
      for job in jobs_by_time[time]:
        active_staff[job.staff_member.id()].append(job)
      for staff, jobs in active_staff.iteritems():
        if not jobs:
          continue
        contains_current_time = False
        for job in jobs:
          if job.heat.get().start_time == time:
            contains_current_time = True
            break
        if contains_current_time:
          continue
        output['all_assignments'].append({
            'staff_member': jobs[0].staff_member.get(),
            'jobs': jobs,
        })
        active_staff[staff] = []
    for staff, jobs in active_staff.iteritems():
      if jobs:
        output['all_assignments'].append({
            'staff_member': jobs[0].staff_member.get(),
            'jobs': jobs,
        })
    self.response.write(JINJA_ENVIRONMENT.get_template('job_schedule.html').render(output))
