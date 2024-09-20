# Dev Assessment - Webhook Receiver

Please use this repository for constructing the Flask webhook receiver.

*******************

## Setup

* Create the virtual env

```bash
python -m venv venv
```

* Activate the virtual env

```bash
venv\Scripts\activate
```

* Install requirements

```bash
pip install -r requirements.txt
```

* Run the flask application (In production, please use Gunicorn)

```bash
flask --app app run
```

* Expose application using ngrok (For testing purposes)

```bash
ngrok http 5000

```

* The endpoints is at:

```bash
To receive a webhook, send a POST request to http://<ngrok-app-url>/webhooks/reciever
To display the received webhooks, send a GET request to http://<ngrok-app-url>/webhooks/recieved
```

*******************