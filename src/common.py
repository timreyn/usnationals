def DatetimeToDict(datetime):
  return {
      'year' : datetime.year,
      'month' : datetime.month,
      'day' : datetime.day,
      'hour' : datetime.hour,
      'minute' : datetime.minute,
      'weekday' : datetime.weekday(),
  }
