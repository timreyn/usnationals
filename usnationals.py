import webapp2

from src import admin
from src import get_competitors
from src import schedule

app = webapp2.WSGIApplication([
    webapp2.Route(r'/get_schedule/<person_id:\d*>', handler=schedule.GetSchedule, name='get_schedule'),
    webapp2.Route('/get_competitors', handler=get_competitors.GetCompetitors, name='get_competitors'),
    webapp2.Route('/admin/add_data', handler=admin.AddData, name='add_data'),
], debug=True)
