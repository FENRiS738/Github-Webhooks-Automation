import datetime
import pytz
from flask import Blueprint, request, render_template
from ..connections import mongo

webhook = Blueprint('Webhook', __name__, url_prefix='/webhooks')

@webhook.get('/recieved')
def get_stored_data():
    events = list(mongo.db.events.find())
    for event in events:
        event['_id'] = str(event['_id'])
        event['timestamp'] = event['timestamp'].astimezone(pytz.utc).strftime('%d %B %Y - %I:%M %p UTC')
        if event['action'] == 'push':
            event['message'] = f'{event["author"]} pushed to "{event["to_branch"]}" on {event["timestamp"]}'
        elif event['action'] == 'pull_request':
            event['message'] = f'{event["author"]} submitted a pull request from "{event["from_branch"]}" to "{event["to_branch"]}" on {event["timestamp"]}'

    return render_template('data.html', events=events)



@webhook.post('/reciever')
def get_webhook_data():
    event = request.headers.get('X-GitHub-Event')
    data: dict = request.get_json()

    if event == 'push':
        response = create_push_event(data, event)
        if 'error' in response:
            return {"error": response.get('error')}, 400
    if event == 'pull_request' and data.get('action') == 'opened':
        response = create_pull_request_event(data, event)
        if 'error' in response:
            return {"error": response.get('error')}, 400

    return {"success": "Data inserted successfully"}, 200


def create_push_event(data: dict, event: str):
    try:
        request_id = data.get('head_commit', {}).get('id')
        author = data.get('pusher', {}).get('name')
        ref = data.get('ref', "")
        timestamp = data.get('head_commit', {}).get('timestamp')

        if not all([request_id, author, ref, timestamp]):
            return {"error": "Missing required data in the payload"}

        record = {
            "request_id": request_id,
            "author": author,
            "action": event,
            "from_branch": ref.split('/')[-1],
            "to_branch": ref.split('/')[-1],
            "timestamp": datetime.datetime.fromisoformat(timestamp).astimezone(pytz.utc)
        }
        mongo.db.events.insert_one(record)
        return {"success": "ok"}

    except Exception as ex:
        return {"error": f"An error occurred: {str(ex)}"}


def create_pull_request_event(data: dict, event: str):
    try:
        request_id = data.get('pull_request', {}).get('id')
        author = data.get('pull_request', {}).get('user', {}).get('login')
        from_branch = data.get('pull_request', {}).get('head', {}).get('ref')
        to_branch = data.get('pull_request', {}).get('base', {}).get('ref')
        timestamp = data.get('pull_request', {}).get('updated_at')

        if not all([request_id, author, event, from_branch, to_branch, timestamp]):
            return {"error": "Missing required data in the payload"}

        record = {
            "request_id": request_id,
            "author": author,
            "action": event,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": datetime.datetime.fromisoformat(timestamp).astimezone(pytz.utc)
        }

        mongo.db.events.insert_one(record)
        return {"success": "ok"}

    except Exception as ex:
        return {"error": f"An error occurred: {str(ex)}"}
