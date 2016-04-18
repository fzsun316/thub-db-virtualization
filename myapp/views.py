from myapp import app
from services import Traffic, Weather
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

@app.route('/calWeatherData')
def calWeatherData():
	t = Weather()
	t.aggregate()
	return "str(stdout)"

@app.route('/calTrafficData')
def calTrafficData():
	t = Traffic()
	t.aggregate()
	return "str(stdout)"

@app.route('/api/trafficData')
def trafficData():
	t = Traffic()
	result = t.loadCurrentSummary()
	js = json.dumps(result)
	resp = Response(js, status=200, mimetype='application/json')
	return resp

@app.route('/api/weatherData')
def weatherData():
	t = Weather()
	result = t.loadCurrentSummary()
	js = json.dumps(result)
	resp = Response(js, status=200, mimetype='application/json')
	return resp
