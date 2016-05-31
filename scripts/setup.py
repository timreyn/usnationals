from google.appengine.ext import ndb

import datetime

from src.models import *

def AddStages():
  for stage in Stage.query().iter():
    stage.key.delete()

  for name in ('Red', 'Blue', 'Green', 'Orange'):
    Stage(id = name[0].lower(), name = name).put()

def AddEvents(real_events=True):
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
    event = Event.get_by_id(event_id) or Event(id = event_id)
    event.name = event_name
    event.priority = priority
    event.is_real = real_events
    event_key = event.put()
    priority += 1

    for i in range(num_rounds):
      round_id = Round.Id(event_id, i + 1)
      round = Round.get_by_id(round_id) or Round(id = round_id)
      round.event = event_key
      round.number = i + 1
      round.is_final = (i == num_rounds - 1)
      round.put()

def AddHeat(event_and_round, stage, number, start_minutes, end_minutes, day):
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
  heat_id = Heat.Id(event_id, round_id, stage, number)

  heat = Heat.get_by_id(heat_id) or Heat(id = heat_id)
  heat.round = round.key
  heat.stage = Stage.get_by_id(stage).key
  heat.number = number
  heat.start_time = start_time
  heat.end_time = end_time
  heat.put()

def AddCompetitor(cusa_id, wca_id, name, is_staff):
  cusa_id = str(cusa_id)
  competitor = Competitor.get_by_id(cusa_id) or Competitor(id = cusa_id)
  competitor.name = name
  competitor.wca_id = wca_id
  competitor.is_staff = is_staff == 1
  competitor.is_admin = False
  competitor.put()

def AssignHeat(event, round, stage, heat, person_id):
  person_id = str(person_id)
  assignment_id = HeatAssignment.Id(event, round, person_id)
  assignment = HeatAssignment.get_by_id(assignment_id) or HeatAssignment(id = assignment_id)

  assignment.heat = Heat.get_by_id(Heat.Id(event, round, stage, heat))
  assignment.competitor = Competitor.get_by_id(person_id).key
  assignment.put()
