from myapp import app
from services import Traffic
import json
from bson import json_util
from bson.json_util import dumps
import ast
from flask import Response, Flask, render_template

@app.route('/')
def index():
    return "hello"

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route('/calTrafficData')
def test():
	t = Traffic()
	t.aggregate()
	return "str(stdout)"

@app.route('/trafficData')
def trafficData():
	t = Traffic()
	result = t.loadCurrentSummary()
	js = json.dumps(result)
	resp = Response(js, status=200, mimetype='application/json')
	return resp
