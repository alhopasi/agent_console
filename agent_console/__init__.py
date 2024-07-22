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

try:
    with app.app_context():
        db.create_all()
        #admin_user = User(user="admin", password="kissa123", nation="", alliance="", role="admin")
        #db.session.add(admin_user)
        #db.commit()
except Exception as e:
    print(e)
    pass
