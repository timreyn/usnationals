from src.admin.assignments import scorers

def AssignmentScore(competitor, assignments, state):
  previous_heat = None
  current_heat = None
  score = 1.0

  for assignment in sorted(assignments, key=lambda assignment: assignment.heat.get().start_time):
    previous_heat = current_heat
    current_heat = assignment.heat.get()
    for scorer in scorers.GetScorers():
      subscore = scorer.Score(current_heat, previous_heat, competitor, state)
      if subscore < scorer.GetMinimumScore():
        subscore = scorer.GetMinimumScore()
      if subscore > 1.0:
        subscore = 1.0
      score *= subscore
  return score
