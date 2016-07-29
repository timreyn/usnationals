from twilio.rest import TwilioRestClient

from src.models import TwilioConfig

def SendSMS(heat_assignment, subscriber):
  heat = heat_assignment.heat.get()
  message = 'It\'s time for %s to compete in %s on the %s stage!' % (
      heat_assignment.competitor.get().name,
      heat.round.get().event.get().name,
      heat.stage.get().name)
  twilio_config = TwilioConfig.get_by_id("1")
  if not twilio_config:
    raise Exception('No twilio config found!')
  print twilio_config
  twilio_client = TwilioRestClient(twilio_config.account_sid, twilio_config.auth_token)
  twilio_client.messages.create(body=message, to=subscriber.phone_number, from_=twilio_config.phone_number)

def SendStaffSMS(staff_assignment, subscriber):
  job = {
    'J': 'Judge at station %d' % (staff_assignment.station or 0),
    'S': 'Scramble',
    'R': 'Run',
    'D': 'do Data Entry',
    'H': 'work at the Help Desk',
    'L': 'Judge in the long room',
    'U': 'Scramble in the long room',
  }[staff_assignment.job]
  message = 'It\'s time for %s to %s' % (staff_assignment.staff_member.get().name, job)
  twilio_config = TwilioConfig.get_by_id("1")
  if not twilio_config:
    raise Exception('No twilio config found!')
  print twilio_config
  twilio_client = TwilioRestClient(twilio_config.account_sid, twilio_config.auth_token)
  twilio_client.messages.create(body=message, to=subscriber.phone_number, from_=twilio_config.phone_number)
