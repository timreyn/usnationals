from google.appengine.ext import ndb

from src import common
from src.models.competitor import Competitor
from src.models.admin_device import AdminDevice
from src.models.round import Round
from src.models.stage import Stage

class Heat(ndb.Model):
  round = ndb.KeyProperty(kind=Round)
  stage = ndb.KeyProperty(kind=Stage)
  number = ndb.IntegerProperty()
  start_time = ndb.DateTimeProperty()
  end_time = ndb.DateTimeProperty()
  call_time = ndb.DateTimeProperty()
  call_device = ndb.KeyProperty(kind=AdminDevice)

  @staticmethod
  def Id(event_id, round_id, stage, number):
    return '%s_%s_%d' % (Round.Id(event_id, round_id), stage, number)

  def ToDict(self):
    output = {
        'id' : self.key.id(),
        'round' : self.round.get().ToDict(),
        'stage' : self.stage.get().ToDict(),
        'number' : self.number,
        'start_time' : common.DatetimeToDict(self.start_time),
        'end_time' : common.DatetimeToDict(self.end_time),
    }
    if self.call_time:
      output['call_time'] = common.DatetimeToDict(self.call_time)
    return output


class HeatAssignment(ndb.Model):
  heat = ndb.KeyProperty(kind=Heat)
  competitor = ndb.KeyProperty(kind=Competitor)

  @staticmethod
  def Id(event_id, round_number, person_id):
    return '%s_%s' % (Round.Id(event_id, round_number), person_id)

  @staticmethod
  def Id(round_id, person_id):
    return '%s_%s' % (round_id, person_id)
