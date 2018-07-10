from src import common

def FormatGroupStartTime(start_time):
  return start_time.strftime('%a %H:%M')

def FormatCompetitorBirthday(birthday):
  return birthday.strftime('%Y-%m-%d')

def FormatTime(event_registration):
  using_average = common.ShouldUseAverage(event_registration.event.id())
  if using_average:
    time = event_registration.average
  else:
    time = event_registration.single
  return common.FormatTime(time, event_registration.event.id(), using_average)
