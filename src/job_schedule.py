import collections
import webapp2

from src.jinja import JINJA_ENVIRONMENT
from src.models import StaffAssignment
from src.models import Stage

class JobSchedule(webapp2.RequestHandler):
  def get(self):
    job = self.request.get('job')
    if not job:
      return 'no job found'
    assignments_query = StaffAssignment.query(StaffAssignment.job == job)
    stage = None
    stage_id = self.request.get('stage')
    if stage_id:
      stage = Stage.get_by_id(stage_id)
    station = None
    if self.request.get('station'):
      station = int(self.request.get('station'))
      assignments_query = assignments_query.filter(StaffAssignment.station == station)
    job_name = {
        'J': 'Judging',
        'S': 'Scrambling',
        'R': 'Running',
        'H': 'Help Desk',
        'D': 'Data Entry',
        'L': 'Judge (Long)',
        'U': 'Scramble (Long)',
    }[job]
    title = job_name
    if stage:
      title += ' %s Stage' % stage.name
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
      if stage and heat.stage.id() != stage_id:
        continue
      jobs_by_time[heat.start_time].append(staff_assignment)
    for day in (7, 8, 9):
      active_staff = collections.defaultdict(list)
      for time in sorted(jobs_by_time.keys()):
        if time.day != day:
          continue
        for job in jobs_by_time[time]:
          active_staff[job.staff_member.id()].append(job)
        for staff, jobs in active_staff.iteritems():
          if not jobs:
            continue
          contains_current_time = False
          for job in jobs:
            if job.heat.get().end_time >= time:
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
