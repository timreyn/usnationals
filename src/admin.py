import csv
import datetime
import StringIO
import webapp2

from src import firebase
from src.jinja import JINJA_ENVIRONMENT
from src.models import *

class AddData(webapp2.RequestHandler):
  def post(self):
    memfile = StringIO.StringIO(self.request.get('data'))
    result = self.ReadData(memfile)
    template = JINJA_ENVIRONMENT.get_template('add_data.html')
    self.response.write(template.render({
        'data' : self.request.get('data'),
        'result' : result,
        'path' : webapp2.uri_for('add_data'),
    }))

  def get(self):
    template = JINJA_ENVIRONMENT.get_template('add_data.html')
    self.response.write(template.render({
        'path' : webapp2.uri_for('add_data'),
    }))

  def ReadData(self, memfile):
    for row in csv.reader(memfile):
      if not row:
        continue
      if row[0] == 'stage':
        if len(row) != 4:
          return 'Bad row ' + row
        stage_id = row[1]
        stage_name = row[2]
        color_hex = row[3]
        AddStage(stage_id, stage_name, color_hex)
      elif row[0] == 'event':
        if len(row) != 6:
          return 'Bad event ' + row
        event_id = row[1]
        event_name = row[2]
        num_rounds = int(row[3])
        is_real = bool(row[4])
        priority = int(row[5])
        AddEvent(event_id, event_name, num_rounds, is_real, priority)
      elif row[0] == 'heat':
        if len(row) != 8:
          return 'Bad heat ' + row
        event_id = row[1]
        round_id = int(row[2])
        stage = row[3]
        number = int(row[4])
        start_minutes = int(row[5])
        end_minutes = int(row[6])
        day = int(row[7])
        ret_value = AddHeat(event_id, round_id, stage, number, start_minutes, end_minutes, day)
        if ret_value != 'ok':
          return 'Bad heat ' + str(row) + ': ' + ret_value
      elif row[0] == 'competitor':
        if len(row) != 5:
          return 'Bad competitor ' + row
        cusa_id = row[1]
        wca_id = row[2]
        name = row[3]
        is_staff = bool(row[4])
        AddCompetitor(cusa_id, wca_id, name, is_staff)
      elif row[0] == 'heat_assignment':
        if len(row) != 6:
          return 'Bad heat assignment ' + row
        event_id = row[1]
        round_id = int(row[2])
        stage = row[3]
        heat = int(row[4])
        person_id = row[5]
        ret_value = AssignHeat(event_id, round_id, stage, heat, person_id)
        if ret_value != 'ok':
          return 'Bad heat assignment ' + str(row) + ': ' + ret_value
    return 'Success!'

def AddStage(stage_id, stage_name, color_hex):
  stage = Stage.get_by_id(stage_id) or Stage(id = stage_id)
  stage.name = stage_name
  stage.color_hex = color_hex
  stage.put()

def AddEvent(event_id, event_name, num_rounds, is_real, priority):
  event = Event.get_by_id(event_id) or Event(id = event_id)
  event.name = event_name
  event.priority = priority
  event.is_real = is_real
  event_key = event.put()
  priority += 1

  for i in range(num_rounds):
    round_id = Round.Id(event_id, i + 1)
    round = Round.get_by_id(round_id) or Round(id = round_id)
    round.event = event_key
    round.number = i + 1
    round.is_final = (i == num_rounds - 1)
    round.put()

def AddHeat(event_id, round_id, stage, number, start_minutes, end_minutes, day):
  round = Round.get_by_id(Round.Id(event_id, round_id))
  if not round:
    return 'Couldn\'t find a round with event %s and number %d' % (event_id, round_id)
  start_hours = start_minutes / 60
  start_minutes = start_minutes % 60
  end_hours = end_minutes / 60
  end_minutes = end_minutes % 60
  start_time = datetime.datetime(2016, 7, day, start_hours, start_minutes, 0)
  end_time = datetime.datetime(2016, 7, day, end_hours, end_minutes, 0)
  heat_id = Heat.Id(event_id, round_id, stage, number)

  heat = Heat.get_by_id(heat_id) or Heat(id = heat_id)
  heat.round = round.key
  heat.stage = Stage.get_by_id(stage).key
  heat.number = number
  heat.start_time = start_time
  heat.end_time = end_time
  heat.put()
  return 'ok'

def AddCompetitor(cusa_id, wca_id, name, is_staff):
  cusa_id = str(cusa_id)
  competitor = Competitor.get_by_id(cusa_id) or Competitor(id = cusa_id)
  competitor.name = name
  competitor.wca_id = wca_id
  competitor.is_staff = is_staff == 1
  competitor.is_admin = False
  competitor.put()

def AssignHeat(event, round, stage, heat, person_id):
  person_id = str(person_id)
  assignment_id = HeatAssignment.Id(event, round, person_id)
  assignment = HeatAssignment.get_by_id(assignment_id) or HeatAssignment(id = assignment_id)
  heat_id = Heat.Id(event, round, stage, heat)

  heat = Heat.get_by_id(heat_id)
  if not heat:
    return 'Could not find heat ' + heat_id
  competitor = Competitor.get_by_id(person_id)
  if not competitor:
    return 'Could not find competitor ' + person_id
  assignment.heat = heat.key
  assignment.competitor = competitor.key
  assignment.put()
  return 'ok'

class SetFirebaseKey(webapp2.RequestHandler):
  # This should really be a POST...but it's easier this way.
  def get(self, key):
    firebase_key = FirebaseKey.get_by_id('1') or FirebaseKey(id = '1')
    firebase_key.f_key = key
    firebase_key.put()
    self.response.write('Success!')

class EditUsers(webapp2.RequestHandler):
  def post(self):
    user_password = self.request.get('password')
    is_admin = self.request.get('is_admin') != ''
    competitor_id = self.request.get('competitor')
    competitor = Competitor.get_by_id(competitor_id)
    if not competitor:
      raise Exception('No matching competitor found!')

    devices = AdminDevice.query(AdminDevice.password == user_password).iter()
    devices_found = False
    for device in devices:
      device.competitor = competitor.key
      if not device.is_authorized and is_admin:
        device.authorized_time = datetime.datetime.now()
        self.NotifyDevice(device, is_admin)
      if device.is_authorized and not is_admin:
        device.deauthorized_time = datetime.datetime.now()
        self.NotifyDevice(device, is_admin)
      device.is_authorized = is_admin
      device.put()
      devices_found = True
    if not devices_found:
      raise Exception('No matching devices found!')
    self.WriteOutput()

  def get(self):
    self.WriteOutput()

  def WriteOutput(self):
    template = JINJA_ENVIRONMENT.get_template('edit_users.html')
    devices = AdminDevice.query().order(-AdminDevice.creation_time).iter()
    competitors = [competitor for competitor in Competitor.query().iter()]
    self.response.write(template.render({
        'devices': devices,
        'competitors': competitors,
        'path' : webapp2.uri_for('edit_users'),
    }))

  def NotifyDevice(self, device, is_admin):
    data = {'isAdmin': '1' if is_admin else '0',
            'deviceId': device.key.id(),
            'competitorName': device.competitor.get().name,
           }
    topic = '/topics/device_' + device.key.id()
    firebase.SendPushNotification(topic, data, 'adminStatus')
