from src.models import HeatAssignment

import collections
import math


def GetRoundNumber(r):
  if r.event.id() in ('333fm', '333mbf'):
    return 1
  return r.number


class AssignmentState(object):

  def __init__(self):
    # round id to list of Heats
    self.heats = collections.defaultdict(list)
    # round id to Round
    self.rounds = {}
    # competitor id to Competitor
    self.competitors = {}
    self.start_time = None
    self.end_time = None

    # competitor id to list of EventRegistrations (registered)
    self.registered_events = collections.defaultdict(list)
    # event id to list of EventRegistrations (registered)
    self.competitors_by_event = collections.defaultdict(list)

    # heat id to list of Competitors (assigned)
    self.competitors_by_heat = collections.defaultdict(list)

    # round id to desired number of Competitors
    self.desired_competitors = collections.defaultdict(lambda: 0)
    # done competitor ids
    self.finished_competitors = set()

    # futures to be waited on before finishing
    self.futures = []


  def Finish(self):
    for future in self.futures:
      future.get_result()


  def RegisterHeat(self, h):
    self.heats[h.round.id()].append(h)
    if h.round.id() not in self.rounds:
      self.rounds[h.round.id()] = h.round.get()
    if h.number > 0:
      if not self.start_time or h.start_time < self.start_time:
        self.start_time = h.start_time
      if not self.end_time or h.end_time > self.end_time:
        self.end_time = h.end_time


  def RegisterCompetitorForEvent(self, event_registration):
    self.registered_events[event_registration.competitor.id()].append(event_registration)
    self.competitors_by_event[event_registration.event.id()].append(event_registration)
    self.competitors[event_registration.competitor.id()] = event_registration.competitor.get()


  def FinalizeEntryList(self):
    for round_id, heats in self.heats.iteritems():
      # figure out how many people should be in each heat
      r = self.rounds[round_id]
      has_staff_heats = len([h for h in heats if h.number == 0]) > 0
      if GetRoundNumber(r) > 1:
        total = r.num_competitors * 1.5
      else:
        if has_staff_heats:
          total = len([reg for reg in self.competitors_by_event[r.event.id()] if not reg.competitor.get().is_staff])
        else:
          total = len(self.competitors_by_event[r.event.id()])
      num_heats = len([h for h in heats if h.number > 0])
      desired = int(math.ceil(1.0 * total / num_heats))
      self.desired_competitors[round_id] = desired

      # figure out which competitors might advance
      if GetRoundNumber(r) > 1:
        by_single = lambda reg: reg.single
        by_average = lambda reg: reg.average
        competitors_sorted = sorted(self.competitors_by_event[r.event.id()],
                                    key=(by_single if 'bf' in r.event.id() or 'fm' in r.event.id() else by_average))
        for i, competitor in enumerate(competitors_sorted):
          if i < total:
            competitor.projected_rounds = max(competitor.projected_rounds, GetRoundNumber(r))
          else:
            competitor.projected_rounds = min(competitor.projected_rounds, GetRoundNumber(r) - 1)
          futures.append(competitor.put_async())


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
    event_id_to_registration = {}
    for event_registration in self.registered_events[competitor.key.id()]:
      event_id_to_registration[event_registration.event.id()] = event_registration
    return event_id_to_registration


  def GetCompetitorRounds(self, competitor):
    output = []
    event_registrations = self.GetCompetitorRegistrations(competitor)
    for r in self.rounds.itervalues():
      if r.event.id() not in event_registrations:
        continue
      reg = event_registrations[r.event.id()]
      if reg.projected_rounds >= r.number:
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
    staff_heats = []
    non_staff_heats = []
    for h in self.heats[r.key.id()]:
      if h.number == 0:
        staff_heats.append(h)
      else:
        non_staff_heats.append(h)
    if competitor.is_staff and staff_heats:
      return staff_heats
    else:
      return non_staff_heats
