import webapp2

from src import admin
from src import schedule

app = webapp2.WSGIApplication([
    webapp2.Route('/get_schedule/(\d*)', handler=schedule.GetSchedule),
    webapp2.Route('/admin/add_data', handler=admin.AddData, name='add_data'),
], debug=True)
