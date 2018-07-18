import datetime

from google.appengine.ext import ndb

from src.admin.assignments.assignment_score import AssignmentScore
from src.admin.assignments.assignment_score import AssignmentScoreDebug
from src.admin.assignments.assignment_state import AssignmentState
from src.admin.assignments.busy_score import BusyScore
from src.models import ActiveAssignment
from src.models import DebugInfo
from src.models import EventRegistration
from src.models import Group
from src.models import GroupAssignment

import random

def PopulateState(state, rounds):
  done_events = set()
  for r in rounds:
    for h in Group.query(Group.round == r.key).iter():
      state.RegisterGroup(h)
    if r.event.id() not in done_events:
      for reg in EventRegistration.query(EventRegistration.event == r.event).iter():
        state.RegisterCompetitorForEvent(reg)
    done_events.add(r.event.id())
  state.FinalizeEntryList()


def GetNextCompetitor(state):
  best_score = 0.0
  best_competitor = None
  for competitor in state.GetCompetitors():
    score = BusyScore(competitor, state)
    if score >= best_score:
      best_score = score
      best_competitor = competitor
  return best_competitor


def GetGroupAssignments(competitor, state, rounds, assignments = [], best_score = 0.0, incoming_score = 1.0):
  if not rounds:
    return assignments, incoming_score
  best_assignments = []
  groups = state.AllGroups(competitor, rounds[0])
  random.shuffle(groups)
  group_and_score = []
  considered_times = set()
  used_times = set()
  for assignment in assignments:
    time = assignment.start_time
    while time < assignment.end_time:
      used_times.add(time)
      time += datetime.timedelta(minutes=5)
  for group in groups:
    if group.start_time in considered_times:
      continue
    def tostr(g):
      return '%s: %s' % (g.key.id(), g.start_time.strftime('%H:%M'))
    if group.start_time in used_times:
      #print 'Rejecting %s' % tostr(group)
      continue
    score = AssignmentScore(competitor, assignments + [group], state)
    #print '%s: [%s]: %.02f' % (competitor.name, ','.join(tostr(k) for k in assignments + [group]), score)
    if len(rounds) == 1 and score == incoming_score:
      return assignments + [group], score
    # If the new group has a perfect score, recurse right now.
    if score == incoming_score:
      considered_times.add(group.start_time)
      new_assignments, new_score = GetGroupAssignments(competitor, state, rounds[1:], assignments + [group], best_score, incoming_score)
      # If this group was optimal, or the total assignment was good enough, return.
      if new_score == incoming_score or new_score >= 0.5:
        return new_assignments, new_score
      if new_score > best_score:
        best_assignments = new_assignments
        best_score = new_score
    else:
      # Otherwise, add it to the queue.
      group_and_score.append([group, AssignmentScore(competitor, assignments + [group], state)])
  for group, intermediate_score in sorted(group_and_score, key=lambda x: x[1], reverse=True):
    if intermediate_score <= best_score or intermediate_score == 0.0:
      continue
    if group.start_time in considered_times:
      continue
    considered_times.add(group.start_time)
    if len(rounds) == 1:
      new_assignments, new_score = assignments + [group], intermediate_score
    else:
      new_assignments, new_score = GetGroupAssignments(competitor, state, rounds[1:], assignments + [group], best_score, intermediate_score)
    # If this group was optimal, or the total assignment was good enough, return.
    if new_score == incoming_score or new_score >= 0.5:
      return new_assignments, new_score
    if new_score > best_score:
      best_assignments = new_assignments
      best_score = new_score
  if not best_assignments:
    return [], 0.0
  return best_assignments, best_score
  

# Main method for group assignment.
def AssignGroups(rounds, request_id):
  print request_id
  active_assignment = ActiveAssignment.get_by_id('1')
  if not active_assignment or active_assignment.request_id != request_id:
    return
  state = AssignmentState()
  debug_info = DebugInfo.get_by_id(request_id) or DebugInfo(id=request_id)

  round_to_key = {}
  for i, r in enumerate(rounds):
    round_to_key[r.key.id()] = i

  # Clear existing groups
  futures = []
  for r in rounds:
    for h in Group.query(Group.round == r.key).iter():
      futures.extend(ndb.delete_multi_async(GroupAssignment.query(GroupAssignment.group == h.key).iter(keys_only=True)))
  for future in futures:
    future.get_result()

  # Load data into the state
  PopulateState(state, rounds)

  while state.HasMoreCompetitors():
    competitor = GetNextCompetitor(state)
    print 'Assigning ' + competitor.name
    rounds = sorted(state.GetCompetitorRounds(competitor), key = lambda r: round_to_key[r.key.id()])
    #rounds = sorted(state.GetCompetitorRounds(competitor), key = lambda r: r.group_length, reverse=True)
    group_assignments, score = GetGroupAssignments(competitor, state, rounds)
    if score == 0.0:
      print competitor.name
      print 'Failed!'
      break
    for group in group_assignments:
      state.AssignGroup(competitor, group)
    state.SaveCompetitorDebug(competitor, AssignmentScoreDebug(competitor, group_assignments, state))
    state.FinishCompetitor(competitor)
    debug_info.info = state.DebugInfo()
    debug_info.put()
  print 'Success!!'
  state.Finish()
