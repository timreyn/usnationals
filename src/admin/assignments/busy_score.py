# Defines a score representing how busy a competitor's schedule is for a
# particular time period, and how high priority it is to schedule them.
def BusyScore(competitor, state):
  competitor_rounds = state.GetCompetitorRounds(competitor)
  rounds = state.GetAllRounds()
  total_time = state.GetTotalTime()

  for r in rounds:
    if r not in competitor_rounds:
      continue
    if r.event.id() == '333fm':
      continue
    registration = event_registrations[r.event.id()]
    if r.number > registration.projected_rounds:
      continue
    score += r.heat_length * 1.0 / total_time

    available_heats = state.GetAvailableHeats(competitor, r)
    if len(available_heats):
      score += 1.0 / len(available_heats)
    else:
      score += 2.0
  return score
