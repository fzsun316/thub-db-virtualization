from flask_apscheduler import APScheduler
import datetime

class Config(object):
    JOBS = [
    	{
            'id': 'aggregator_heartbeat',
            'func': 'myapp.services:request_heartbeat',
            'args': (),
            'trigger': 'interval',
            'seconds': 3600
        }
    ]

    SCHEDULER_VIEWS_ENABLED = True
