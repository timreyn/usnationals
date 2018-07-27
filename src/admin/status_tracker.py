from google.appengine.api import users

import collections
import datetime
import webapp2

from src.jinja import JINJA_ENVIRONMENT
from src.models import Group
from src.models import Stage

GRAY_R = 128
GRAY_G = 128
GRAY_B = 128
GREEN_R = 0
GREEN_G = 255
GREEN_B = 0
RED_R = 255
RED_G = 0
RED_B = 0
MIDDLE = 0
FULL_GREEN = -600
FULL_RED = 600

def scale(fraction, zero, one):
  if fraction < 0:
    return zero
  if fraction > 1:
    return one
  return int( (1-fraction) * zero + fraction * one)

class Formatters(object):
  @staticmethod
  def FormatTime(group):
    return datetime.datetime.strftime(group.start_time, '%I:%M %p').lstrip('0')

  @staticmethod
  def FormatGroup(group):
    return '%s Group %d' % (group.round.get().event.get().name, group.number)

  @staticmethod
  def DeltaColor(group):
    if not group.call_time:
      return '#000000'
    total_seconds_delta = (group.call_time - group.start_time).total_seconds()
    # HACK HACK HACK HACK i messed up time zones
    total_seconds_delta = total_seconds_delta + 1 * 60 * 60
    if total_seconds_delta < MIDDLE:
      fraction = float(MIDDLE - total_seconds_delta)/(MIDDLE - FULL_GREEN)
      R = scale(fraction, GRAY_R, GREEN_R)
      G = scale(fraction, GRAY_G, GREEN_G)
      B = scale(fraction, GRAY_B, GREEN_B)
    else:
      fraction = float(MIDDLE - total_seconds_delta)/(MIDDLE - FULL_RED)
      R = scale(fraction, GRAY_R, RED_R)
      G = scale(fraction, GRAY_G, RED_G)
      B = scale(fraction, GRAY_B, RED_B)
    return '#%02x%02x%02x' % (R, G, B)

  @staticmethod
  def FormatDelta(group):
    if not group.call_time:
      return ''
    total_seconds_delta = (group.call_time - group.start_time).total_seconds()
    total_seconds_delta = total_seconds_delta + 1 * 60 * 60
    total_seconds_delta_abs = abs(total_seconds_delta)
    minutes = total_seconds_delta_abs / 60
    seconds = total_seconds_delta_abs % 60
    if total_seconds_delta < 0:
      return '-%d:%02d' % (minutes, seconds)
    if total_seconds_delta > 0:
      return '+%d:%02d' % (minutes, seconds)
    return '+0:00'

class StatusTracker(webapp2.RequestHandler):
  def get(self):
    day = int(self.request.get('day'))
    if not day:
      day = 7
    start_time = datetime.datetime(2018, 7, day, 0, 0, 0)
    end_time = datetime.datetime(2018, 7, day, 23, 59, 0)
    groups_by_hour_and_stage = collections.defaultdict(lambda: collections.defaultdict(list))
    all_hours = set()
    for group in Group.query().filter(Group.start_time > start_time).filter(Group.start_time < end_time).iter():
      groups_by_hour_and_stage[group.start_time.hour][group.stage.id()].append(group)
    for hour in groups_by_hour_and_stage:
      for stage in groups_by_hour_and_stage[hour]:
        groups_by_hour_and_stage[hour][stage].sort(key=lambda group: group.start_time)
        all_hours.add(hour)
    all_stages = [Stage.get_by_id(s) for s in ('r', 'b', 'g', 'o', 'y')]
    template = JINJA_ENVIRONMENT.get_template('status_tracker.html')
    all_days = [
        (26, 'Thursday', day == 26),
        (27, 'Friday', day == 27),
        (28, 'Saturday', day == 28),
        (29, 'Sunday', day == 29),
    ]
    self.response.write(template.render({
        'group_dict': groups_by_hour_and_stage,
        'all_stages': all_stages,
        'path': webapp2.uri_for('status_tracker'),
        'uri_for': webapp2.uri_for,
        'all_hours': all_hours,
        'all_days': all_days,
        'Formatters': Formatters,
        'is_admin': users.is_current_user_admin(),
    }))    
