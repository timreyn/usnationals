import webapp2

from src import current_heat
from src import get_competitors
from src import get_heat_info
from src import get_stages
from src import job_schedule
from src import register_device
from src import schedule
from src import scorecards
from src import send_notification
from src import stage_schedule
from src import twiml
from src.admin import add_data
from src.admin import assign_heats
from src.admin import assign_stations
from src.admin import clear_notifications
from src.admin import edit_users
from src.admin import set_firebase_key
from src.admin import status_tracker
from src.admin.assignments import handler as assignments_handler
from src.admin.assignments import debug_handler as assignments_debug_handler

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
    webapp2.Route('/scorecards', handler=scorecards.GetScorecards),
    webapp2.Route(r'/send_notification' +
                  r'/<event_id:.*>/<round_id:\d*>/<stage_id:.*>/<heat_number:\d*>',
                  handler=send_notification.SendNotification),
    webapp2.Route('/job_schedule', handler=job_schedule.JobSchedule),
    webapp2.Route('/twiml', handler=twiml.Twiml),
    webapp2.Route(r'/current_heat/<stage_id:.>', handler=current_heat.CurrentHeat),
    webapp2.Route('/admin/add_data', handler=add_data.AddData, name='add_data'),
    webapp2.Route(r'/admin/assign_stations/<stage_id:.>', handler=assign_stations.AssignStations),
    webapp2.Route('/admin/edit_users', handler=edit_users.EditUsers, name='edit_users'),
    webapp2.Route(r'/admin/set_firebase_key/<key:.*>', handler=set_firebase_key.SetFirebaseKey),
    webapp2.Route('/admin/clear_notifications', handler=clear_notifications.ClearNotifications),
    webapp2.Route('/status_tracker', handler=status_tracker.StatusTracker, name='status_tracker'),
    webapp2.Route('/admin/assign_later_heats', handler=assign_heats.AssignHeats, name='assign_heats'),
    webapp2.Route('/admin/assign_heats', handler=assignments_handler.AssignmentsHandler),
    webapp2.Route('/admin/assign_heats_debug/<request_id:.*>', handler=assignments_debug_handler.AssignmentsDebugHandler, name='assign_heats_debug'),
], debug=True)
