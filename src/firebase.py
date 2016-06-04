import httplib
import json

from src.models import FirebaseKey

def SendPushNotification(topic, data, message_type):
  firebase_key = FirebaseKey.query().get()
  if not firebase_key:
    raise Exception('No firebase credentials found!')
  headers = {'Content-Type': 'application/json',
             'Authorization': 'key=' + firebase_key.f_key}
  conn = httplib.HTTPSConnection('fcm.googleapis.com')
  data['type'] = message_type
  request = {'to': topic,
             'data': data}
  conn.request('POST', '/fcm/send', json.dumps(request), headers)
  return conn.getresponse()
