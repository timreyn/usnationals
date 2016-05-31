import webapp2

from src import schedule

app = webapp2.WSGIApplication([
    ('/get_schedule/(\d*)', schedule.GetSchedule),
], debug=True)
