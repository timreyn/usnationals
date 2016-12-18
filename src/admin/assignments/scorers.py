class Scorer(object):
  def GetName(self):
    return "UNNAMED"

  # previous_heat may be None if this is the first heat of the time period.
  def Score(self, heat, previous_heat, competitor, state):
    return 0.0

  def GetMinimumScore(self):
    return 1.0


class TimeBetweenHeatsScorer(Scorer):
  def GetName(self):
    return "time_between"

  def Score(self, heat, previous_heat, competitor, state):
    if not previous_heat:
      return 1.0

    time_between_heats = heat.start_time - previous_heat.start_time
    expected_time = heat.round.get().expected_time
    spare_time = time_between_heats - expected_time
    if spare_time < 0:
      return 0.0
    if spare_time < 5:
      return 0.3
    if spare_time < 10:
      return 0.6
    if spare_time < 15:
      return 0.8
    if spare_time < 20:
      return 0.9
    if spare_time < 25:
      return 0.95
    return 1.0

  def GetMinimumScore():
    return 0.0


class NumCompetitorsScorer(Scorer):
  def GetName(self):
    return "num_competitors"

  def Score(self, heat, previous_heat, competitor, state):
    expected_count = state.GetDesiredHeatSize(heat.round.get())
    actual_count = len(state.GetCompetitorsInHeat(heat))
    spots_left = expected_count - actual_count

    if spots_left >= 3:
      return 1.0
    if spots_left == 2:
      return 0.95
    if spots_left == 1:
      return 0.9
    if spots_left == 0:
      return 0.4
    if spots_left == -1:
      return 0.2
    if spots_left == -2:
      return 0.1
    return 0.0

  def GetMinimumScore():
    return 0.0


def GetScorers():
  return [
      TimeBetweenHeatsScorer(),
      NumCompetitorsScorer(),
  ]
