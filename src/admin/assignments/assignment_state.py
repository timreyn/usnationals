from src import common
from src.models import HeatAssignment

import collections
import json
import math


def GetRoundNumber(r):
  if r.event.id() in ('333fm', '333mbf'):
    return 1
  return r.number


class AssignmentState(object):

  def __init__(self):
    # round id to list of Heats
    self.staff_heats = collections.defaultdict(list)
    self.non_staff_heats = collections.defaultdict(list)
    # round id to Round
    self.rounds = {}
    # competitor id to Competitor
    self.competitors = {}
    self.start_time = None
    self.end_time = None

    # competitor id to dict of eventid to EventRegistrations (registered)
    self.registered_events = collections.defaultdict(dict)
    # event id to list of EventRegistrations (registered)
    self.competitors_by_event = collections.defaultdict(list)

    # heat id to list of Competitors (assigned)
    self.competitors_by_heat = collections.defaultdict(list)

    # round id to desired number of Competitors
    self.desired_competitors = collections.defaultdict(lambda: 0)
    # done competitor ids
    self.finished_competitors = set()
    # competitor id to dict
    self.competitor_debug = {}

    # futures to be waited on before finishing
    self.futures = []


  def Finish(self):
    for future in self.futures:
      future.get_result()


  def RegisterHeat(self, h):
    if h.number == 0:
      self.staff_heats[h.round.id()].append(h)
    else:
      self.non_staff_heats[h.round.id()].append(h)
      if not self.start_time or h.start_time < self.start_time:
        self.start_time = h.start_time
      if not self.end_time or h.end_time > self.end_time:
        self.end_time = h.end_time
    if h.round.id() not in self.rounds:
      self.rounds[h.round.id()] = h.round.get()


  def RegisterCompetitorForEvent(self, event_registration):
    self.registered_events[event_registration.competitor.id()][event_registration.event.id()] = event_registration
    self.competitors_by_event[event_registration.event.id()].append(event_registration)
    self.competitors[event_registration.competitor.id()] = event_registration.competitor.get()


  def FinalizeEntryList(self):
    for round_id, heats in self.non_staff_heats.iteritems():
      # figure out how many people should be in each heat
      r = self.rounds[round_id]
      has_staff_heats = round_id in self.staff_heats
      if GetRoundNumber(r) > 1:
        total = r.num_competitors * 1.5
      else:
        if has_staff_heats:
          total = len([reg for reg in self.competitors_by_event[r.event.id()] if not reg.competitor.get().is_staff])
        else:
          total = len(self.competitors_by_event[r.event.id()])
      num_heats = len(heats)
      desired = int(math.ceil(1.0 * total / num_heats))
      self.desired_competitors[round_id] = desired

      # figure out which competitors might advance
      by_single = lambda reg: reg.single
      by_average = lambda reg: reg.average
      competitors_sorted = sorted(self.competitors_by_event[r.event.id()],
                                    key=(by_average if common.ShouldUseAverage(r.event.id()) else by_single))
      non_staff_rank = 0
      for i, competitor in enumerate(competitors_sorted):
        if GetRoundNumber(r) > 1:
          if i < total:
            competitor.projected_rounds = max(competitor.projected_rounds, GetRoundNumber(r))
          else:
            competitor.projected_rounds = min(competitor.projected_rounds, GetRoundNumber(r) - 1)
        else:
          if not competitor.competitor.get().is_staff:
            non_staff_rank = non_staff_rank + 1
            competitor.non_staff_rank = non_staff_rank
        self.futures.append(competitor.put_async())


  def HasMoreCompetitors(self):
    return len(self.registered_events) > len(self.finished_competitors)


  def GetCompetitors(self):
    return [self.competitors[c] for c in self.registered_events if c not in self.finished_competitors]


  def FinishCompetitor(self, competitor):
    self.finished_competitors.add(competitor.key.id())


  def GetAllRounds(self):
    return self.rounds.values()


  def GetTotalTime(self):
    return (self.end_time - self.start_time).total_seconds() / 60


  def GetDesiredHeatSize(self, r):
    return self.desired_competitors[r.key.id()]


  def GetCompetitorsInHeat(self, heat):
    return self.competitors_by_heat[heat.key.id()]


  def GetCompetitorRegistrations(self, competitor):
    return self.registered_events[competitor.key.id()]


  def GetCompetitorRounds(self, competitor):
    output = []
    event_registrations = self.GetCompetitorRegistrations(competitor)
    for r in self.rounds.itervalues():
      if r.event.id() not in event_registrations:
        continue
      reg = event_registrations[r.event.id()]
      if reg.projected_rounds >= GetRoundNumber(r):
        output.append(r)
    return output


  def AssignHeat(self, competitor, heat):
    self.competitors_by_heat[heat.key.id()].append(competitor)
    if GetRoundNumber(heat.round.get()) == 1:
      assignment_id = HeatAssignment.Id(heat.round.id(), competitor.key.id())
      heat_assignment = HeatAssignment.get_by_id(assignment_id) or HeatAssignment(id = assignment_id)
      heat_assignment.heat = heat.key
      heat_assignment.competitor = competitor.key
      self.futures.append(heat_assignment.put_async())


  def GetAvailableHeats(self, competitor, r):
    all_heats = self.AllHeats(competitor, r)
    desired = self.desired_competitors[r.key.id()]
    return [h for h in all_heats if h.number == 0 or len(self.competitors_by_heat[h.key.id()]) < desired]


  def AllHeats(self, competitor, r):
    if competitor.is_staff and r.key.id() in self.staff_heats:
      return self.staff_heats[r.key.id()]
    else:
      return self.non_staff_heats[r.key.id()]


  def SaveCompetitorDebug(self, competitor, debug):
    self.competitor_debug[competitor.key.id()] = debug


  def DebugInfo(self):
    heats_by_competitor = collections.defaultdict(list)
    for h, cs in self.competitors_by_heat.iteritems():
      for c in cs:
        heats_by_competitor[c.key.id()].append(h)
    return json.dumps({
        'r': self.rounds.keys(),
        'r2h': {r: [h.key.id() for h in hs] for r, hs in self.non_staff_heats.iteritems()},
        'h2c': {h: [c.key.id() for c in cs] for h, cs in self.competitors_by_heat.iteritems()},
        'r2n': self.desired_competitors,
        'd': self.competitor_debug})
