import pytz

def DatetimeToDict(datetime):
  return {
      'year' : datetime.year,
      'month' : datetime.month,
      'day' : datetime.day,
      'hour' : datetime.hour,
      'minute' : datetime.minute,
      'weekday' : datetime.weekday(),
  }

def FormatTime(value, eventId, average=False):
  if value == -2:
    return 'DNS'
  if value == -1:
    return 'DNF'
  if value == 0:
    return ''
  if eventId == '333fm' and not average:
    return str(value)
  if eventId == '333mbf' or (eventId == '333mbo' and value < 10 ** 9):
    difference = 99 - (value / (10 ** 7))
    value = value % (10 ** 7)
    timeInSeconds = value / (10 ** 2)
    missed = value % (10 ** 2)
    solved = difference + missed
    attempted = missed + solved
    if timeInSeconds == 99999:
      timeString = '??'
    else:
      timeString = FormatTime(timeInSeconds * 100, '333mbf_time')
    return '%d/%d (%s)' % (solved, attempted, timeString)
  if eventId == '333mbo':
    value -= 10 ** 9
    solved = 99 - value / (10 ** 7)
    value = value % (10 ** 7)
    attempted = value / (10 ** 5)
    timeInSeconds = value % (10 ** 5)
    if timeInSeconds == 99999:
      timeString = '??'
    else:
      timeString = FormatTime(timeInSeconds * 100, '333mbo_time')
    return '%d/%d (%s)' % (solved, attempted, timeString)
  hundredths = value % 100
  seconds = (value / 100) % 60
  minutes = (value / (100 * 60)) % 60
  hours = value / (100 * 60 * 60)
  showHundredths = eventId not in ('333mbf_time', '333mbo_time')
  hundredthsString = '.%.02d' % hundredths if showHundredths else ''
  if hours > 0:
    return '%d:%02d:%02d%s' % (hours, minutes, seconds, hundredthsString)
  if minutes > 0:
    return '%d:%02d%s' % (minutes, seconds, hundredthsString)
  return '%01d%s' % (seconds, hundredthsString)

def ShouldUseAverage(eventId):
  return eventId not in ['333bf', '444bf', '555bf', '333mbf', '333fm']

TZ = pytz.timezone('America/New_York')
