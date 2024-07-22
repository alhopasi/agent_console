from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///agentconsole.db"

db = SQLAlchemy(app)

from agent_console import models
from agent_console.models import User
from agent_console import main


from os import urandom
app.config["SECRET_KEY"] = urandom(32)

from flask_login import LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

try:
    with app.app_context():
        db.create_all()
except Exception as e:
    print(e)
    pass
