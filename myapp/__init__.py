from flask import Flask
app = Flask(__name__)

#APScheduler
from flask_apscheduler import APScheduler
from myapp.jobs import Config
app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)

from myapp import views