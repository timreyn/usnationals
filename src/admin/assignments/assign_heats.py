from src.admin.assignments.assignment_score import AssignmentScore
from src.admin.assignments.assignment_state import AssignmentState
from src.admin.assignments.busy_score import BusyScore
from src.models import EventRegistration
from src.models import Heat

def PopulateState(state, rounds):
  for r in rounds:
    for h in Heat.query(Heat.round == r.key).iter():
      state.RegisterRound(h)
    for reg in EventRegistration.query(EventRegistration.event == r.event).iter():
      state.RegisterCompetitorForEvent(reg)
  state.FinalizeEntryList()


def GetNextCompetitor(state):
  best_score = 0.0
  best_competitor = None
  for competitor in state.GetCompetitors():
    score = BusyScore(competitor, state)
    if score > best_score:
      best_score = score
      best_competitor = competitor
  return best_competitor


def GetHeatAssignments(competitor, state, rounds, assignments = [], best_score = 0.0):
  if not rounds:
    return assignments, AssignmentScore(competitor, assignments, state)
  best_assignments = []
  for heat in state.AllHeats(competitor, rounds[0]):
    intermediate_score = AssignmentScore(competitor, assignments + [heat], state)
    if intermediate_score < best_score:
      continue
    new_assignments, new_score = GetHeatAssignments(competitor, state, rounds[1:], assignments + [heat], best_score)
    if new_score > best_score:
      best_assignments = new_assignments
      best_score = new_score
  if not best_assignments:
    return [], 0.0
  return best_assignments, best_score
  

# Main method for heat assignment.
def AssignHeats(rounds, request_id):
  state = AssignmentState()

  # Clear existing heats
  futures = []
  for r in rounds:
    futures.append(ndb.delete_multi_async(HeatAssignment.query(HeatAssignment.round == r.key).iter(keys_only=True)))
  for future in futures:
    future.get_result()

  # Load data into the state
  PopulateState(state, rounds)

  while state.HasMoreCompetitors():
    competitor = GetNextCompetitor(state)
    rounds = sorted(state.GetCompetitorRounds(competitor), key = lambda r: r.heat_length)
    heat_assignments, score = GetHeatAssignments(competitor, state, rounds)
    if score == 0.0:
      # add failure debug info
      break
    for heat in heat_assignments:
      state.AssignHeat(competitor, heat)
    state.FinishCompetitor(competitor)
  state.Finish()
