import collections
import datetime
import webapp2

from src.jinja import JINJA_ENVIRONMENT
from src.models import Heat
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
  def FormatTime(heat):
    return datetime.datetime.strftime(heat.start_time, '%I:%M %p').lstrip('0')

  @staticmethod
  def FormatHeat(heat):
    return '%s Heat %d' % (heat.round.get().event.get().name, heat.number)

  @staticmethod
  def DeltaColor(heat):
    if not heat.call_time:
      return '#000000'
    total_seconds_delta = (heat.call_time - heat.start_time).total_seconds()
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
  def FormatDelta(heat):
    if not heat.call_time:
      return ''
    total_seconds_delta = abs((heat.call_time - heat.start_time).total_seconds())
    minutes = total_seconds_delta / 60
    seconds = total_seconds_delta % 60
    if heat.call_time < heat.start_time:
      return '-%d:%02d' % (minutes, seconds)
    if heat.call_time > heat.start_time:
      return '+%d:%02d' % (minutes, seconds)
    return '+0:00'

class StatusTracker(webapp2.RequestHandler):
  def get(self):
    day = int(self.request.get('day'))
    if not day:
      day = 29
    start_time = datetime.datetime(2017, 7, day, 0, 0, 0)
    end_time = datetime.datetime(2017, 7, day, 23, 59, 0)
    heats_by_hour_and_stage = collections.defaultdict(lambda: collections.defaultdict(list))
    all_hours = set()
    for heat in Heat.query().filter(Heat.start_time > start_time).filter(Heat.start_time < end_time).iter():
      heats_by_hour_and_stage[heat.start_time.hour][heat.stage.id()].append(heat)
    for hour in heats_by_hour_and_stage:
      for stage in heats_by_hour_and_stage[hour]:
        heats_by_hour_and_stage[hour][stage].sort(key=lambda heat: heat.start_time)
        all_hours.add(hour)
    all_stages = [Stage.get_by_id(s) for s in ('r', 'b', 'g', 'o', 'y')]
    template = JINJA_ENVIRONMENT.get_template('status_tracker.html')
    all_days = [
        (6, 'Thursday', day == 6),
        (7, 'Friday', day == 7),
        (8, 'Saturday', day == 8),
        (9, 'Sunday', day == 9),
    ]
    self.response.write(template.render({
        'heat_dict': heats_by_hour_and_stage,
        'all_stages': all_stages,
        'path': webapp2.uri_for('status_tracker'),
        'all_hours': all_hours,
        'all_days': all_days,
        'Formatters': Formatters,
    }))    
