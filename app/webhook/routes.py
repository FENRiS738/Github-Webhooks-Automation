import datetime
import pytz
from flask import Blueprint, request, render_template
from ..connections import mongo

webhook = Blueprint('Webhook', __name__, url_prefix='/webhooks')


# Endpoint to get all webhooks event call details and displays them on frontend  
@webhook.get('/recieved')
def get_stored_data():
    # Extracting all the data from the database
    events = list(mongo.db.events.find().sort('timestamp', -1))

    # Generating a list of dictionaries to be passed to the frontend
    for event in events:
        event['_id'] = str(event['_id'])
        event['timestamp'] = event['timestamp'].astimezone(pytz.utc).strftime('%d %B %Y - %I:%M %p UTC')
        if event['action'] == 'push':
            event['message'] = f'{event["author"]} pushed to "{event["to_branch"]}" on {event["timestamp"]}'
        elif event['action'] == 'pull_request':
            event['message'] = f'{event["author"]} submitted a pull request from "{event["from_branch"]}" to "{event["to_branch"]}" on {event["timestamp"]}'
    
    return render_template('index.html', events=events)

# Endpoint to accept push and pull request webhooks event calls
@webhook.post('/reciever')
def get_webhook_data():
    event = request.headers.get('X-GitHub-Event')
    data: dict = request.get_json()

    # Checking if the event is a push or pull request event
    if event == 'push':
        response = create_push_event(data, event)
        if 'error' in response:
            return {"error": response.get('error')}, 400
    if event == 'pull_request' and data.get('action') == 'opened':
        response = create_pull_request_event(data, event)
        if 'error' in response:
            return {"error": response.get('error')}, 400

    return {"success": "Data inserted successfully"}, 200


# Method to store push event data in MongoDB
def create_push_event(data: dict, event: str):
    try:
        request_id = data.get('head_commit', {}).get('id')
        author = data.get('pusher', {}).get('name')
        ref = data.get('ref', "")
        timestamp = data.get('head_commit', {}).get('timestamp')

        # Checking if the data is valid
        if not all([request_id, author, ref, timestamp]):
            return {"error": "Missing required data in the payload"}

        # Creating a new document for events collection
        record = {
            "request_id": request_id,
            "author": author,
            "action": event,
            "from_branch": ref.split('/')[-1],
            "to_branch": ref.split('/')[-1],
            "timestamp": datetime.datetime.fromisoformat(timestamp).astimezone(pytz.utc)
        }

        # Inserting data into MongoDB
        mongo.db.events.insert_one(record)
        return {"success": "ok"}

    except Exception as ex:
        return {"error": f"An error occurred: {str(ex)}"}

# Method to store pull request event data in MongoDB
def create_pull_request_event(data: dict, event: str):
    try:
        request_id = data.get('pull_request', {}).get('id')
        author = data.get('pull_request', {}).get('user', {}).get('login')
        from_branch = data.get('pull_request', {}).get('head', {}).get('ref')
        to_branch = data.get('pull_request', {}).get('base', {}).get('ref')
        timestamp = data.get('pull_request', {}).get('updated_at')

        # Checking if the data is valid
        if not all([request_id, author, event, from_branch, to_branch, timestamp]):
            return {"error": "Missing required data in the payload"}

        # Creating a new document for events collection
        record = {
            "request_id": request_id,
            "author": author,
            "action": event,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": datetime.datetime.fromisoformat(timestamp).astimezone(pytz.utc)
        }

        # Inserting data into MongoDB
        mongo.db.events.insert_one(record)
        return {"success": "ok"}

    except Exception as ex:
        return {"error": f"An error occurred: {str(ex)}"}
