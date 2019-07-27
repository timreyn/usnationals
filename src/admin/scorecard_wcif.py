import collections
import json
import webapp2

from google.appengine.ext import ndb

from src.models import Competitor
from src.models import EventRegistration
from src.models import Group
from src.models import GroupAssignment
from src.models import Round
from src.models import Stage

def RoundName(r):
  if r.is_final:
    return '%s Final' % r.event.get().name
  return '%s Round %d' % (r.event.get().name, r.number)

def GroupName(g):
  if g.staff:
    return 'S%d' % g.number
  return '%d' % g.number

def RoundActivityCode(r):
  if r.event.id() in ['333fm']:
    return '%s-r1-a%d' % (r.event.id(), r.number)
  return '%s-r%d' % (r.event.id(), r.number)

def GroupActivityCode(g):
  if g.staff:
    return '%s-gS%d' % (RoundActivityCode(g.round.get()), g.number)
  return '%s-g%d' % (RoundActivityCode(g.round.get()), g.number)

class ScorecardWcifHandler(webapp2.RequestHandler):
  def get(self):
    out = {
      'formatVersion': '1.0',
      'id': 'CubingUSANationals2019',
      'name': 'CubingUSA Nationals 2019',
      'shortName': 'CubingUSA Nationals 2019',
      'persons': [],
      'schedule': {
        'startDate': '2019-08-01',
        'numberOfDays': 1,
        'venues': [
          {
            'id': 1,
            'rooms': [
              {
                'id': 1,
                'name': 'Main Room',
                'activities': [],
              },
            ],
          }
        ],
      },
      "extensions": [
      {
        "id": "groupifier.CompetitionConfig",
        "specUrl": "https://jonatanklosko.github.io/groupifier-next/wcif-extensions/CompetitionConfig.json",
        "data": {
          "localNamesFirst": False,
          "scorecardsBackgroundUrl": "",
          "competitorsSortingRule": "symmetric",
          "noTasksForNewcomers": False,
          "tasksForOwnEventsOnly": True
        }
      }],

    }
    stage = self.request.get('s')
    use_stars = stage in ('r', 'b')
    rounds = self.request.get('r').split(',')
    events = [r[:-2] for r in rounds]
    round_to_id = {}
    id_to_event = {}
    sched = out['schedule']['venues'][0]['rooms'][0]['activities']
    for i, r in enumerate(rounds):
      sched.append({
        'id': i,
        'name': RoundName(Round.get_by_id(r)),
        'activityCode': RoundActivityCode(Round.get_by_id(r)),
        #'startTime': '2100-01-01',
        #'endTime': '1970-01-01',
        'childActivities': [],
      })
      round_to_id[r] = i
    next_id = len(rounds)
    group_to_id = {}
    all_group_keys = []
    for group in Group.query(Group.stage == ndb.Key(Stage, stage)):
      if group.round.id() not in rounds:
        continue
      r = sched[round_to_id[group.round.id()]]
      r['childActivities'].append({
        'id': next_id,
        'name': GroupName(group),
        'activityCode': GroupActivityCode(group),
      })
      group_to_id[group.key.id()] = next_id
      id_to_event[next_id] = group.round.get().event.id()
      next_id += 1
      all_group_keys.append(group.key)
      if use_stars and not group.staff:
        r['childActivities'].append({
          'id': next_id,
          'name': GroupName(group) + 'X',
          'activityCode': GroupActivityCode(group) + 'X'})
        group_to_id[group.key.id() + 'X'] = next_id
        next_id += 1
        all_group_keys.append(group.key.id() + 'X')

    assignments_by_competitor = collections.defaultdict(list)
    events_by_competitor = collections.defaultdict(list)
    registrations_by_competitor = collections.defaultdict(dict)
    registrations_by_group = collections.defaultdict(dict)

    for assignment in GroupAssignment.query().iter():
      if assignment.group not in all_group_keys:
        continue
      assignments_by_competitor[assignment.competitor.id()].append({
        'activityId': group_to_id[assignment.group.id()],
        'assignmentCode': 'competitor',
      })
      event_id = assignment.group.get().round.get().event.id()
      events_by_competitor[assignment.competitor.id()].append(event_id)
      if not assignment.group.get().staff:
        registrations_by_group[assignment.group.id()][assignment.competitor.id()] = None

    if use_stars:
      for registration in EventRegistration.query().iter():
        event_id = registration.event.id()
        if registration.event.id() not in events:
          continue
        for group_id, registrations in registrations_by_group.iteritems():
          if not group_id.startswith(event_id + "_"):
            continue
          if registration.competitor.id() not in registrations:
            continue
          registrations[registration.competitor.id()] = registration

      # keyed by event_id
      competitors_to_star = collections.defaultdict(list)
      for group_id, registrations in registrations_by_group.iteritems():
        for person_id, r in registrations.iteritems():
          if not r:
            print 'Couldn\'t find ' + person_id + ' in ' + group_id
        if Group.get_by_id(group_id).staff:
          continue
        competitors_to_star[group_id.split("_")[0]] += [
            registration.competitor.id() for registration in
            sorted(registrations.values(), key=lambda r: r.average)[:3]]

      for competitor_id, assignments in assignments_by_competitor.iteritems():
        for assignment in assignments:
          event_id = id_to_event[assignment['activityId']]
          if competitor_id in competitors_to_star[event_id]:
            assignment['activityId'] += 1

    for competitor in Competitor.query().iter():
      if competitor.key.id() not in events_by_competitor:
        continue
      out['persons'].append({
        'name': competitor.name,
        'wcaId': competitor.wca_id,
        'registrantId': competitor.key.id(),
        'assignments': assignments_by_competitor[competitor.key.id()],
        'registration': {
          'eventIds': events_by_competitor[competitor.key.id()],
          'status': 'accepted',
        },
        'personalBests': [],
        'extensions': [],
      })

    out['events'] = json.loads("""
    [
    {
      "id": "222",
      "rounds": [
        {
          "id": "222-r1",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 160
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "222-r2",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 64
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "222-r3",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 16
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "222-r4",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": null,
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        }
      ],
      "extensions": [

      ]
    },
    {
      "id": "333",
      "rounds": [
        {
          "id": "333-r1",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 200
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "333-r2",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 80
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "333-r3",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 16
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "333-r4",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": null,
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        }
      ],
      "extensions": [

      ]
    },
    {
      "id": "333bf",
      "rounds": [
        {
          "id": "333bf-r1",
          "format": "3",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 16
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "333bf-r2",
          "format": "3",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": null,
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        }
      ],
      "extensions": [

      ]
    },
    {
      "id": "333fm",
      "rounds": [
        {
          "id": "333fm-r1",
          "format": "m",
          "timeLimit": null,
          "cutoff": null,
          "advancementCondition": null,
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        }
      ],
      "extensions": [

      ]
    },
    {
      "id": "333ft",
      "rounds": [
        {
          "id": "333ft-r1",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": null,
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        }
      ],
      "extensions": [

      ]
    },
    {
      "id": "333mbf",
      "rounds": [
        {
          "id": "333mbf-r1",
          "format": "2",
          "timeLimit": null,
          "cutoff": null,
          "advancementCondition": null,
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        }
      ],
      "extensions": [

      ]
    },
    {
      "id": "333oh",
      "rounds": [
        {
          "id": "333oh-r1",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 64
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "333oh-r2",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 16
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "333oh-r3",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": null,
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        }
      ],
      "extensions": [

      ]
    },
    {
      "id": "444",
      "rounds": [
        {
          "id": "444-r1",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 100
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "444-r2",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 48
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "444-r3",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 16
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "444-r4",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": null,
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        }
      ],
      "extensions": [

      ]
    },
    {
      "id": "444bf",
      "rounds": [
        {
          "id": "444bf-r1",
          "format": "3",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": null,
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        }
      ],
      "extensions": [

      ]
    },
    {
      "id": "555",
      "rounds": [
        {
          "id": "555-r1",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 48
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "555-r2",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 16
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "555-r3",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": null,
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        }
      ],
      "extensions": [

      ]
    },
    {
      "id": "555bf",
      "rounds": [
        {
          "id": "555bf-r1",
          "format": "3",
          "timeLimit": {
            "centiseconds": 120000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": null,
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        }
      ],
      "extensions": [

      ]
    },
    {
      "id": "666",
      "rounds": [
        {
          "id": "666-r1",
          "format": "m",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 16
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "666-r2",
          "format": "m",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": null,
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        }
      ],
      "extensions": [

      ]
    },
    {
      "id": "777",
      "rounds": [
        {
          "id": "777-r1",
          "format": "m",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 16
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "777-r2",
          "format": "m",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": null,
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        }
      ],
      "extensions": [

      ]
    },
    {
      "id": "clock",
      "rounds": [
        {
          "id": "clock-r1",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 16
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "clock-r2",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": null,
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        }
      ],
      "extensions": [

      ]
    },
    {
      "id": "minx",
      "rounds": [
        {
          "id": "minx-r1",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 48
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "minx-r2",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 16
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "minx-r3",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": null,
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        }
      ],
      "extensions": [

      ]
    },
    {
      "id": "pyram",
      "rounds": [
        {
          "id": "pyram-r1",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 100
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "pyram-r2",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 48
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "pyram-r3",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 16
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "pyram-r4",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": null,
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        }
      ],
      "extensions": [

      ]
    },
    {
      "id": "skewb",
      "rounds": [
        {
          "id": "skewb-r1",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 64
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "skewb-r2",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 16
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "skewb-r3",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": null,
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        }
      ],
      "extensions": [

      ]
    },
    {
      "id": "sq1",
      "rounds": [
        {
          "id": "sq1-r1",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 48
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "sq1-r2",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": {
            "type": "ranking",
            "level": 16
          },
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        },
        {
          "id": "sq1-r3",
          "format": "a",
          "timeLimit": {
            "centiseconds": 60000,
            "cumulativeRoundIds": [

            ]
          },
          "cutoff": null,
          "advancementCondition": null,
          "scrambleSetCount": 1,
          "results": [

          ],
          "extensions": [

          ]
        }
      ],
      "extensions": [

      ]
    }
  ]""")

    self.response.content_type = 'application/json'
    self.response.write(json.dumps(out))
