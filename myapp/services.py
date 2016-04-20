import pymongo
from pymongo import MongoClient
import datetime
from myapp import scheduler
import time
import requests
import smtplib	# email
import thread
import logging
logging.basicConfig()

# MONGODB_HOST = 'localhost'
MONGODB_HOST = '129.59.107.160'
MONGODB_PORT = 27017
connection = MongoClient(MONGODB_HOST, MONGODB_PORT)

class PublicAPI:

	TIMEZONEDIFF = 1800

	def __init__(self):
		pass

	def sampleToDay(self, timestamp):
		# diff = (timestamp-self.TIMEZONEDIFF+24*3600)%(24*3600)
		diff = timestamp%3600
		return timestamp-diff

publicAPI = PublicAPI()

def request_heartbeat():
	hb = HeartBeat()
	thread.start_new_thread(hb.accessToAggregator, ())
	# hb = HeartBeat()
	# hb.accessToAggregator()

def check_traffic_status():
	t = Traffic()
	thread.start_new_thread(t.aggregate, ())
	# t.aggregate()

def check_weather_status():
	print 'check_weather_status'
	t = Weather()
	thread.start_new_thread(t.aggregate, ())
	# t.aggregate()

class HeartBeat:
	AGR_TEST_URL = "http://129.59.107.160:5000/scheduler/jobs"

	def __init__(self):
		pass

	def accessToAggregator(self):
		try:
		    r = requests.get(self.AGR_TEST_URL)
		    print "-> heartbeat from aggregator"
		except requests.exceptions.RequestException as e:    # This is the correct syntax
		    print e
		    server = smtplib.SMTP('smtp.gmail.com', 587)
		    server.starttls()
		    server.login("thub.service@gmail.com", "Wz123456")
		    sub = "-> Heartbeat Msg from T-HUB Aggregator"
		    text = "The aggregator service may be down. Please check it. Thanks!"
		    message = 'Subject: %s\n\n%s' % (sub, text)
		    server.sendmail("thub.service@gmail.com", "fzsun316@gmail.com", message)
		    server.quit()

class Weather:
	def __init__(self):
		pass

	def loadCurrentSummary(self):
		db_collection = connection["collection-status"]["weather"]
		tpResults = db_collection.find()
		for tpResult in tpResults:
			# print tpResult['summary']
			if 'summary' in tpResult:
				return tpResult['summary']
		return ''

	def saveToMongoDB(self, result):		
		connection["collection-status"].drop_collection('weather')
		db_collection = connection["collection-status"]["weather"]
		db_collection.insert({"summary": result})

	def generateResult(self, map, startTs, endTs):
		result = []
		for ts in range(startTs, endTs+1, 3600):
			result.append({"date":ts, "count":map[ts] if ts in map else 0})
			# result[ts] = map[ts] if ts in map else 0
		return result

	def aggregate(self):
		start_time = time.time()
		index=0
		startTs, endTs = -1, -1
		dateMap = {}
		# connect to realtime traffic data
		db_collection = connection["thub_weather"]["realtime_data"]
		tpResults = db_collection.find()
		totalNum = tpResults.count()
		for tpResult in tpResults:
			if 'currently' in tpResult:
				currently = tpResult['currently']
				if 'time' in currently:
					timestamp = int(currently['time'])
					timestamp = publicAPI.sampleToDay(timestamp)
					# get start and end timestamps
					if startTs==-1:
						startTs, endTs = timestamp, timestamp
					elif timestamp<startTs:
						startTs = timestamp
					elif timestamp>endTs:
						endTs = timestamp
					# add to map
					if timestamp in dateMap:
						dateMap[timestamp] = dateMap[timestamp] + 1
					else:
						dateMap[timestamp] = 0
			index+=1
			print "-> Weather: %d seconds" % ((time.time() - start_time)/index*(totalNum-index))
			
		self.saveToMongoDB( self.generateResult(dateMap, startTs, endTs) )


class Traffic:
	def __init__(self):
		pass

	def loadCurrentSummary(self):
		db_collection = connection["collection-status"]["traffic"]
		tpResults = db_collection.find()
		for tpResult in tpResults:
			# print tpResult['summary']
			if 'summary' in tpResult:
				return tpResult['summary']
		return ''

	def saveToMongoDB(self, result):		
		connection["collection-status"].drop_collection('traffic')
		db_collection = connection["collection-status"]["traffic"]
		db_collection.insert({"summary": result})

	def generateResult(self, map, startTs, endTs):
		result = []
		for ts in range(startTs, endTs+1, 3600):
			result.append({"date":ts, "count":map[ts] if ts in map else 0})
			# result[ts] = map[ts] if ts in map else 0
		return result

	def aggregate(self):
		start_time = time.time()
		index=0
		startTs, endTs = -1, -1
		dateMap = {}
		# connect to realtime traffic data
		db_collection = connection["thub_traffic"]["realtime_data2"]
		tpResults = db_collection.find()
		totalNum = tpResults.count()
		for tpResult in tpResults:
			traffic = tpResult['traffic']
			# traffic_series =tpResult["traffic_series"]
			# aggregate timestamp to the start of the day
			# for traffic in traffic_series:
			timestamp = int(traffic['request_time'])
			timestamp = publicAPI.sampleToDay(timestamp)
			# get start and end timestamps
			if startTs==-1:
				startTs, endTs = timestamp, timestamp
			elif timestamp<startTs:
				startTs = timestamp
			elif timestamp>endTs:
				endTs = timestamp
			# add to map
			if timestamp in dateMap:
				dateMap[timestamp] = dateMap[timestamp] + 1
			else:
				dateMap[timestamp] = 0
			index+=1
			print "-> Traffic: %d seconds" % ((time.time() - start_time)/index*(totalNum-index))
			
		self.saveToMongoDB( self.generateResult(dateMap, startTs, endTs) )
		

