from google.appengine.ext import ndb

import datetime

from src.models import *

def AddStages():
  for stage in Stage.query().iter():
    stage.key.delete()

  for name in ('Red', 'Blue', 'Green', 'Orange'):
    Stage(id = name[0].lower(), name = name).put()

def AddEvents(real_events=True):
  for event in Event.query(Event.is_real == real_events).iter():
    for round in Round.query(Round.event == event.key).iter():
      round.key.delete()
    event.key.delete()

  priority = 0
  if real_events:
    events = (
      ('333', 'Rubik\'s Cube', 4),
      ('444', '4x4 Cube', 4),
      ('555', '5x5 Cube', 3),
      ('222', '2x2 Cube', 4),
      ('333oh', 'Rubik\'s Cube One-Handed', 4),
      ('333bf', 'Rubik\'s Cube Blindfolded', 2),
      ('333fm', 'Rubik\'s Cube Fewest Moves', 1),
      ('pyram', 'Pyraminx', 4),
      ('skewb', 'Skewb', 3),
      ('minx', 'Megaminx', 2),
      ('sq1', 'Square-1', 2),
      ('clock', 'Rubik\'s Clock', 2),
      ('666', '6x6 Cube', 2),
      ('777', '7x7 Cube', 2),
      ('444bf', '4x4 Cube Blindfolded', 1),
      ('555bf', '5x5 Cube Blindfolded', 1),
      ('333mbf', 'Rubik\'s Cube Multiple Blindfolded', 1),
    )
  else:
    events = (
      ('lunch', 'Lunch', 1),
      ('reg', 'Registration', 1),
    )
  for (event_id, event_name, num_rounds) in events:
    event_key = Event(id = event_id,
                      name = event_name,
                      priority = priority,
                      is_real = real_events).put()
    priority += 1
    for i in range(num_rounds):
      round_id = Round.Id(event_id, i + 1)
      Round(id = round_id,
            event = event_key,
            number = i + 1,
            is_final = (i == num_rounds - 1)).put()

def AddHeat(event_and_round, stage, heat, start_minutes, end_minutes, day):
  if '_' in event_and_round:
    event_id = event_and_round.split('_')[0]
    round_id = int(event_and_round.split('_')[1])
  else:
    event_id = event_and_round
    round_id = 1
  round = Round.get_by_id(Round.Id(event_id, round_id))
  if not round:
    print 'Couldn\'t find a round with event %s and number %d' % (event_id, round_id)
    return
  start_hours = start_minutes / 60
  start_minutes = start_minutes % 60
  end_hours = end_minutes / 60
  end_minutes = end_minutes % 60
  start_time = datetime.datetime(2016, 7, day, start_hours, start_minutes, 0)
  end_time = datetime.datetime(2016, 7, day, end_hours, end_minutes, 0)
  heat_id = Heat.Id(event_id, round_id, stage, heat)
  old_heat = Heat.get_by_id(heat_id)
  if old_heat:
    old_heat.key.delete()
  
  Heat(id = heat_id,
       round = round.key,
       stage = Stage.get_by_id(stage).key,
       number = heat,
       start_time = start_time,
       end_time = end_time).put()

def AssignHeat(event, round, stage, heat, person_id):
  assignment_id = HeatAssignment.Id(event, round, person_id)
  old_assignment = HeatAssignment.get_by_id(assignment_id)
  if old_assignment:
    old_assignment.key.delete()

  HeatAssignment(id = HeatAssignment.Id(event, round, person_id),
                 heat = Heat.get_by_id(Heat.Id(event, round, stage, heat)),
                 competitor = Competitor.get_by_id(person_id)).put()
