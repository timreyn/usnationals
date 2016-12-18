import csv
import datetime
import StringIO
import webapp2

from google.appengine.ext import ndb

from src.jinja import JINJA_ENVIRONMENT
from src.models import *

class AddData(webapp2.RequestHandler):
  def post(self):
    memfile = StringIO.StringIO(self.request.get('data').replace('\t', '').replace(';', '\n'))
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
    futures = []
    for row in csv.reader(memfile):
      if not row:
        continue
      if row[0] == 'stage':
        if len(row) != 4:
          return 'Bad row ' + str(row)
        stage_id = row[1]
        stage_name = row[2]
        color_hex = row[3]
        AddStage(futures, stage_id, stage_name, color_hex)
      elif row[0] == 'event':
        if len(row) != 5:
          return 'Bad event ' + str(row)
        event_id = row[1]
        event_name = row[2]
        is_real = row[3] == '1'
        priority = int(row[4])
        AddEvent(futures, event_id, event_name, is_real, priority)
      elif row[0] == 'round':
        if len(row) != 5 and len(row) != 6:
          return 'Bad round ' + str(row)
        event_id = row[1]
        number = int(row[2])
        is_final = row[3] == '1'
        heat_length = int(row[4])
        num_competitors = int(row[5]) if len(row) > 5 else 0
        ret_value = AddRound(futures, event_id, number, is_final, heat_length, num_competitors)
        if ret_value != 'ok':
          return 'Bad round ' + str(row) + ': ' + ret_value
      elif row[0] == 'heat':
        if len(row) != 8:
          return 'Bad heat ' + str(row)
        event_id = row[1]
        round_id = int(row[2])
        stage = row[3]
        number = int(row[4])
        start_minutes = int(row[5])
        end_minutes = int(row[6])
        day = int(row[7])
        ret_value = AddHeat(futures, event_id, round_id, stage, number, start_minutes, end_minutes, day)
        if ret_value != 'ok':
          return 'Bad heat ' + str(row) + ': ' + ret_value
      elif row[0] == 'competitor':
        if len(row) != 6:
          return 'Bad competitor ' + str(row)
        cusa_id = row[1]
        wca_id = row[2]
        name = row[3]
        is_staff = row[4] == '1'
        date_of_birth = datetime.datetime.strptime(row[5], '%Y-%m-%d').date()
        AddCompetitor(futures, cusa_id, wca_id, name, is_staff, date_of_birth)
      elif row[0] == 'heat_assignment':
        if len(row) != 6:
          return 'Bad heat assignment ' + str(row)
        event_id = row[1]
        round_id = int(row[2])
        stage = row[3]
        heat = int(row[4])
        person_id = row[5]
        ret_value = AssignHeat(futures, event_id, round_id, stage, heat, person_id)
        if ret_value != 'ok':
          return 'Bad heat assignment ' + str(row) + ': ' + ret_value
      elif row[0] == 'staff_assignment':
        if len(row) not in (7, 8, 9):
          return 'Bad staff assignment ' + str(row)
        event_id = row[1]
        round_id = int(row[2])
        stage = row[3]
        heat = int(row[4])
        staff_id = row[5]
        job = row[6]
        long_event = None
        if len(row) >= 8:
          long_event = row[7]
        misc = ''
        if len(row) >= 9:
          misc = row[8]
        ret_value = AddStaffAssignment(futures, event_id, round_id, stage, heat, staff_id, job, long_event, misc)
        if ret_value != 'ok':
          return 'Bad staff assignment ' + str(row) + ': ' + ret_value
      elif row[0] == 'twilio':
        if len(row) != 4:
          return 'Bad twilio data ' + str(row)
        phone_number = row[1]
        account_sid = row[2]
        auth_token = row[3]
        AddTwilioData(futures, phone_number, account_sid, auth_token)
      elif row[0] == 'sms_subscriber':
        if len(row) != 3:
          return 'Bad subscriber ' + str(row)
        phone_number = row[1]
        competitor = int(row[2])
        AddSMSSubscriber(futures, phone_number, competitor)
      elif row[0] == 'event_registration':
        if len(row) != 5:
          return 'Bad event registration ' + str(row)
        competitor_id = int(row[1])
        event_id = int(row[2])
        single = int(row[3])
        average = int(row[4])
        ret_value = AddEventRegistration(futures, competitor_id, event_id, single, average)
        if ret_value != 'ok':
          return 'Bad event registration ' + str(row) + ': ' + ret_value
      elif row[0] == 'DELETE_DATA':
        if len(row) != 2:
          return 'Bad deletion ' + str(row)
        DeleteData(futures, row[1])
      elif row[0] == 'DELETE_STAFF_ASSIGNMENT':
        if len(row) != 2:
          return 'Bad staff assignment deletion ' + str(row)
        DeleteStaffAssignment(futures, row[1])
    for future in futures:
      future.get_result()
    return 'Success!'

def AddStage(futures, stage_id, stage_name, color_hex):
  stage = Stage.get_by_id(stage_id) or Stage(id = stage_id)
  stage.name = stage_name
  stage.color_hex = color_hex
  futures.append(stage.put_async())

def AddEvent(futures, event_id, event_name, is_real, priority):
  event = Event.get_by_id(event_id) or Event(id = event_id)
  event.name = event_name
  event.priority = priority
  event.is_real = is_real
  event_key = event.put()

def AddRound(futures, event_id, number, is_final, heat_length, num_competitors):
  event = Event.get_by_id(event_id)
  if not event:
    return 'Couldn\'t find event ' + event_id
  round_id = Round.Id(event_id, number)
  round = Round.get_by_id(round_id) or Round(id = round_id)
  round.event = event.key
  round.number = number
  round.is_final = is_final
  round.heat_length = heat_length
  futures.append(round.put_async())
  return 'ok'

def AddHeat(futures, event_id, round_id, stage, number, start_minutes, end_minutes, day):
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
  heat.call_time = None
  heat.call_device = None
  futures.append(heat.put_async())
  return 'ok'

def AddCompetitor(futures, cusa_id, wca_id, name, is_staff, date_of_birth):
  cusa_id = str(cusa_id)
  competitor = Competitor.get_by_id(cusa_id) or Competitor(id = cusa_id)
  competitor.name = name
  competitor.wca_id = wca_id
  competitor.is_staff = is_staff == 1
  competitor.is_admin = False
  competitor.date_of_birth = date_of_birth
  futures.append(competitor.put_async())

def AssignHeat(futures, event, round, stage, heat, person_id):
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
  futures.append(assignment.put_async())
  return 'ok'
        
def AddStaffAssignment(futures, event_id, round_id, stage, heat_num, staff_id, job, long_event, misc):
  staff_id = str(staff_id)
  heat_id = Heat.Id(event_id, round_id, stage, heat_num)
  heat = Heat.get_by_id(heat_id)
  if not heat:
    return 'Could not find heat ' + heat_id
  staff_member = Competitor.get_by_id(staff_id)
  if not staff_member:
    return 'Could not find competitor ' + staff_id
  assignment_id = StaffAssignment.Id(event_id, round_id, stage, heat_num, staff_id)
  assignment = StaffAssignment.get_by_id(assignment_id) or StaffAssignment(id = assignment_id)
  assignment.heat = heat.key
  assignment.staff_member = staff_member.key
  assignment.job = job
  if long_event:
    long_event_round_id = Round.Id(long_event, 1)
    long_event_round = Round.get_by_id(long_event_round_id)
    if not long_event_round:
      return 'Could not find event ' + long_event_round_id
    assignment.long_event = long_event_round.key
  if misc:
    assignment.misc = misc
  assignment.station = None
  futures.append(assignment.put_async())
  return 'ok'

def AddTwilioData(futures, phone_number, account_sid, auth_token):
  twilio_config = TwilioConfig.get_by_id("1") or TwilioConfig(id = "1")
  twilio_config.phone_number = phone_number
  twilio_config.account_sid = account_sid
  twilio_config.auth_token = auth_token
  futures.append(twilio_config.put_async())

def AddSMSSubscriber(futures, phone_number, competitor_id):
  competitor = Competitor.get_by_id(str(competitor_id))
  if not competitor:
    return
  subscriber_id = '%s_%d' % (phone_number, competitor_id)
  subscriber = SMSSubscriber.get_by_id(subscriber_id) or SMSSubscriber(id = subscriber_id)
  subscriber.competitor = competitor.key
  subscriber.phone_number = phone_number
  futures.append(subscriber.put_async())

def AddEventRegistration(futures, competitor_id, event_id, single, average):
  competitor = Competitor.get_by_id(str(competitor_id))
  if not competitor:
    return 'Could not find competitor ' + competitor_id
  event = Event.get_by_id(event_id)
  if not event:
    return 'Could not find event ' + event_id
  registration_id = EventRegistration.Id(competitor_id, event_id)
  event_registration = EventRegistration.get_by_id(registration_id) or EventRegistration(id = registration_id)
  event_registration.competitor = competitor.key
  event_registration.event = event.key
  event_registration.single = single
  event_registration.average = average
  event_registration.projected_rounds = 1
  futures.append(event_registration.put_async())

def DeleteData(futures, data_type):
  if data_type == 'stage':
    futures.append(ndb.delete_multi_async(Stage.query().iter(keys_only=True)))
  elif data_type == 'event':
    futures.append(ndb.delete_multi_async(Event.query().iter(keys_only=True)))
    futures.append(ndb.delete_multi_async(Round.query().iter(keys_only=True)))
  elif data_type == 'heat':
    futures.append(ndb.delete_multi_async(Heat.query().iter(keys_only=True)))
  elif data_type == 'competitor':
    futures.append(ndb.delete_multi_async(Competitor.query().iter(keys_only=True)))
  elif data_type == 'heat_assignment':
    futures.append(ndb.delete_multi_async(HeatAssignment.query().iter(keys_only=True)))
  elif data_type == 'staff_assignment':
    futures.append(ndb.delete_multi_async(StaffAssignment.query().iter(keys_only=True)))

def DeleteStaffAssignment(futures, heat_id):
  heat = Heat.get_by_id(heat_id)
  futures.append(ndb.delete_multi_async(StaffAssignment.query(StaffAssignment.heat == heat.key).iter(keys_only=True)))
