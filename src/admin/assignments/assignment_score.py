from src.admin.assignments import scorers

def AssignmentScoreImpl(competitor, assignments, state, is_debug):
  previous_heat = None
  current_heat = None
  score = 1.0
  debug = {}

  for assignment in sorted(assignments, key=lambda assignment: assignment.start_time):
    previous_heat = current_heat
    current_heat = assignment
    if is_debug:
      current_debug = {
          't': current_heat.start_time.isoformat(),
          's': {},
      }
    for scorer in scorers.GetScorers():
      subscore = scorer.Score(current_heat, previous_heat, competitor, state)
      if subscore < scorer.GetMinimumScore():
        subscore = scorer.GetMinimumScore()
      if subscore > 1.0:
        subscore = 1.0
      score *= subscore
      if is_debug:
        current_debug['s'][scorer.GetName()] = subscore
    if is_debug:
      debug[current_heat.key.id()] = current_debug
  return score, debug


def AssignmentScore(competitor, assignments, state):
  score, debug = AssignmentScoreImpl(competitor, assignments, state, False)
  return score


def AssignmentScoreDebug(competitor, assignments, state):
  return AssignmentScoreImpl(competitor, assignments, state, True)
