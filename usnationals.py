import webapp2

from src import cubecomps
from src import current_group
from src import get_competitors
from src import get_group_info
from src import get_stages
from src import job_schedule
from src import printable_schedules
from src import register_device
from src import schedule
from src import scorecards
from src import send_notification
from src import stage_schedule
from src import twiml
from src.admin import add_data
from src.admin import assign_groups
from src.admin import assign_stations
from src.admin import clear_notifications
from src.admin import edit_users
from src.admin import one_offs
from src.admin import scorecard_wcif
from src.admin import set_firebase_key
from src.admin import status_tracker
from src.admin.assignments import handler as assignments_handler
from src.admin.assignments import debug_handler as assignments_debug_handler

app = webapp2.WSGIApplication([
    webapp2.Route(r'/cubecomps/<person_id:\d*>', handler=cubecomps.CubecompsRedirect),
    webapp2.Route(r'/get_schedule/<person_id:\d*>', handler=schedule.GetSchedule),
    webapp2.Route(r'/stage_schedule/<stages:.*>', handler=stage_schedule.GetStageSchedule),
    webapp2.Route('/full_schedule', handler=stage_schedule.GetStageSchedule),
    webapp2.Route('/get_competitors', handler=get_competitors.GetCompetitors),
    webapp2.Route(
        r'/get_group_info/<event_id:.*>/<round_id:\d>/<stage:.>/<number:\d*>',
        handler=get_group_info.GetGroupInfo),
    webapp2.Route('/get_stages', handler=get_stages.GetStages),
    webapp2.Route('/register_device', handler=register_device.RegisterDevice),
    webapp2.Route('/scorecards', handler=scorecards.GetScorecards),
    webapp2.Route(r'/send_notification' +
                  r'/<event_id:.*>/<round_id:\d*>/<stage_id:.*>/<group_number:\d*>',
                  handler=send_notification.SendNotification),
    webapp2.Route(r'/admin/send_notification' +
                  r'/<event_id:.*>/<round_id:\d*>/<stage_id:.*>/<group_number:.*>',
                  handler=send_notification.SendNotification,
                  name='admin_notification'),
    webapp2.Route('/job_schedule', handler=job_schedule.JobSchedule),
    webapp2.Route('/twiml', handler=twiml.Twiml),
    webapp2.Route(r'/current_group/<stage_id:.>', handler=current_group.CurrentGroup),
    webapp2.Route('/printable_schedules', handler=printable_schedules.PrintableSchedulesHandler),
    webapp2.Route('/admin/add_data', handler=add_data.AddData, name='add_data'),
    webapp2.Route(r'/admin/assign_stations/<stage_id:.>', handler=assign_stations.AssignStations),
    webapp2.Route('/admin/edit_users', handler=edit_users.EditUsers, name='edit_users'),
    webapp2.Route(r'/admin/set_firebase_key/<key:.*>', handler=set_firebase_key.SetFirebaseKey),
    webapp2.Route('/admin/clear_notifications', handler=clear_notifications.ClearNotifications),
    webapp2.Route('/status_tracker', handler=status_tracker.StatusTracker, name='status_tracker'),
    webapp2.Route('/admin/assign_later_groups', handler=assign_groups.AssignGroups, name='assign_groups'),
    webapp2.Route('/admin/assign_groups', handler=assignments_handler.AssignmentsHandler),
    webapp2.Route('/admin/assign_groups_debug/<request_id:.*>', handler=assignments_debug_handler.AssignmentsDebugHandler, name='assign_groups_debug'),
    webapp2.Route('/admin/one_off/<name:.*>', handler=one_offs.OneOffHandler),
    webapp2.Route('/admin/scorecard_wcif', handler=scorecard_wcif.ScorecardWcifHandler),
], debug=True)
