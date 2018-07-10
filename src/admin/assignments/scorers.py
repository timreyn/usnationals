import collections

class Scorer(object):
  def GetName(self):
    return "UNNAMED"

  # previous_group may be None if this is the first group of the time period.
  def Score(self, group, previous_group, competitor, state):
    return 0.0

  def GetMinimumScore(self):
    return 1.0


class TimeBetweenGroupsScorer(Scorer):
  def GetName(self):
    return "time_between"

  def Score(self, group, previous_group, competitor, state):
    if not previous_group:
      return 1.0
    if group.number == 0:
      return 1.0

    time_between_groups = group.start_time - previous_group.start_time
    expected_time = previous_group.round.get().group_length
    spare_time = time_between_groups.total_seconds() / 60 - expected_time
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

  def GetMinimumScore(self):
    return 0.0


class NumCompetitorsScorer(Scorer):
  def GetName(self):
    return "num_competitors"

  def Score(self, group, previous_group, competitor, state):
    if group.number == 0:
      return 1.0
    expected_count = state.GetDesiredGroupSize(group.round.get())
    actual_count = len(state.GetCompetitorsInGroup(group))
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

  def GetMinimumScore(self):
    return 0.0


class SpeedScorer(Scorer):
  def GetName(self):
    return "speed"

  def Score(self, group, previous_group, competitor, state):
    if group.number != 1 or competitor.is_staff:
      return 1.0
    expected_count = len(state.AllGroups(competitor, group.round.get()))
    competitor_registration = state.GetCompetitorRegistrations(competitor)[group.round.get().event.id()]
    my_bucket = (competitor_registration.non_staff_rank + 1) / expected_count
    percentile_buckets = collections.defaultdict(lambda: 0)
    for c in state.GetCompetitorsInGroup(group):
      if c.is_staff:
        continue
      other_registration = state.GetCompetitorRegistrations(c)[group.round.get().event.id()]
      percentile_buckets[(other_registration.non_staff_rank + 1) / expected_count]
    competitors_too_close = (self.CompetitorsTooClose(percentile_buckets, my_bucket, True) +
                             self.CompetitorsTooClose(percentile_buckets, my_bucket, False))
    return 0.95 ** competitors_too_close

  def CompetitorsTooClose(self, percentile_buckets, my_bucket, increasing):
    current_bucket = my_bucket
    allowed_competitors = 0
    found_competitors = 0
    while current_bucket >= 0 and current_bucket < len(percentile_buckets):
      found_competitors += percentile_buckets[current_bucket]
      if found_competitors <= allowed_competitors:
        break
      allowed_competitors += 1.5
      if increasing:
        current_bucket += 1
      else:
        current_bucket -= 1
    return found_competitors

  def GetMinimumScore(self):
    return 0.5


def GetScorers():
  return [
      TimeBetweenGroupsScorer(),
      NumCompetitorsScorer(),
#      SpeedScorer(),
  ]
