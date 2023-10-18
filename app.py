import os
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from views import *
from models import db
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True

app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

cors = CORS(app, resources={r"/*": {"origins": "*"}})

api = Api(app)

api.add_resource(ViewSignInUser, "/signin")
api.add_resource(ViewLogin, "/login")
