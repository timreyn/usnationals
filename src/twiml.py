import webapp2

from src.models import Competitor
from src.models import SMSSubscriber

class Twiml(webapp2.RequestHandler):
  def post(self):
    self.response.headers['Content-Type'] = 'text/plain'
    phone_number = self.request.get('From')
    num_subscriptions = len([s for s in SMSSubscriber.query(SMSSubscriber.phone_number == phone_number).iter()])
    msg_split = self.request.get('Body').strip(' ').split(' ')
    if msg_split[0].lower() == 'subscribe' or len(msg_split) == 1:
      if num_subscriptions >= 5:
        self.response.write("Sorry, you can only subscribe to 5 competitors per phone number!")
        return
      wca_id = msg_split[-1]
      competitor = Competitor.query(Competitor.wca_id == wca_id).get()
      if not competitor:
        self.response.write('Sorry, I can\'t find a competitor with ID ' + wca_id)
        return
      num_subscriptions = len([s for s in SMSSubscriber.query(SMSSubscriber.competitor == competitor.key).iter()])
      if num_subscriptions >= 2:
        self.response.write("Sorry, only 2 phone numbers can subscribe to each competitor!")
        return
      subscriber_id = '%s_%s' % (phone_number, wca_id)
      subscriber = SMSSubscriber.get_by_id(subscriber_id) or SMSSubscriber(id = subscriber_id)
      subscriber.phone_number = phone_number
      subscriber.competitor = competitor.key
      subscriber.put()
      self.response.write("Subscribed to texts for %s.  Respond \"unsubscribe %s\" to stop." % (
                              competitor.name, wca_id))
      return
    if msg_split[0].lower() == 'unsubscribe':
      subscriber = SMSSubscriber.get_by_id('%s_%s' % (phone_number, msg_split[-1]))
      if subscriber:
        subscriber.key.delete()
      return
    self.response.write("Sorry, I don't understand.")
