from flask import Flask
from .webhook import webhook
from .connections import init_app

def create_app():
    app = Flask(__name__)

    init_app(app)
    app.register_blueprint(webhook)

    @app.get('/')
    def read_root():
        return {"data": "Server is running..."}, 200

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)