# Defines a score representing how busy a competitor's schedule is for a
# particular time period, and how high priority it is to schedule them.
def BusyScore(competitor, state):
  rounds = state.GetAllRounds()
  total_time = state.GetTotalTime()
  event_registrations = state.GetCompetitorRegistrations(competitor)

  score = 0.0

  for r in rounds:
    if r.event.id() not in event_registrations:
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
