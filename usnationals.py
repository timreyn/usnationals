import webapp2

from src import admin
from src import assign_stations
from src import get_competitors
from src import get_heat_info
from src import get_stages
from src import register_device
from src import send_notification
from src import schedule
from src import stage_schedule

app = webapp2.WSGIApplication([
    webapp2.Route(r'/get_schedule/<person_id:\d*>', handler=schedule.GetSchedule),
    webapp2.Route(r'/stage_schedule/<stages:.*>', handler=stage_schedule.GetStageSchedule),
    webapp2.Route('/full_schedule', handler=stage_schedule.GetStageSchedule),
    webapp2.Route('/get_competitors', handler=get_competitors.GetCompetitors),
    webapp2.Route(
        r'/get_heat_info/<event_id:.*>/<round_id:\d>/<stage:.>/<number:\d*>',
        handler=get_heat_info.GetHeatInfo),
    webapp2.Route('/get_stages', handler=get_stages.GetStages),
    webapp2.Route('/register_device', handler=register_device.RegisterDevice),
    webapp2.Route('/admin/add_data', handler=admin.AddData, name='add_data'),
    webapp2.Route('/admin/assign_stations', handler=assign_stations.AssignStations),
    webapp2.Route('/admin/edit_users', handler=admin.EditUsers, name='edit_users'),
    webapp2.Route(r'/admin/set_firebase_key/<key:.*>', handler=admin.SetFirebaseKey),
    webapp2.Route(r'/admin/send_notification' +
                  r'/<event_id:.*>/<round_id:\d*>/<stage_id:.*>/<heat_number:\d*>',
                  handler=send_notification.SendNotification)
], debug=True)
