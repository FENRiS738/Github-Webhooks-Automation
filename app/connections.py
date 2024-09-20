from flask_pymongo import PyMongo


mongo = PyMongo()

def init_app(app):

    app.config['MONGO_URI'] = "mongodb+srv://as420738:2Z2rqfDK147Ocqsu@webhooks.7r20r.mongodb.net/git-web"

    mongo.init_app(app)