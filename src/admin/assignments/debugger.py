from src.models import DebugInfo

from google.cloud import pubsub

def Debug(state, request_id):
  pubsub_client = pubsub.Client()
  receiving_topic = pubsub_client.topic('request' + request_id)
  sending_topic = pubsub_client.topic('response' + request_id)
  subscription = topic.subscription('subscriber')

  while True:
    results = subscrption.pull(return_immediately=False)
    if results:
      # send state
      sending_topic.publish(state.DebugInfo())
      subscription.acknowledge([ack_id for ack_id, message in results])


def SaveDebugInfo(state, request_id):
  debug_info = DebugInfo(id = request_id)
  debug_info.info = state.DebugInfo()
  debug_info.put()
