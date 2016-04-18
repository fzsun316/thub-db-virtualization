import pymongo
from pymongo import MongoClient
import datetime
from myapp import scheduler
import time

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
		resultMap = {}
		# connect to realtime traffic data
		db_collection = connection["thub_traffic"]["realtime_data"]
		tpResults = db_collection.find()
		totalNum = tpResults.count()
		for tpResult in tpResults:
			traffic_series =tpResult["traffic_series"]
			# aggregate timestamp to the start of the day
			for traffic in traffic_series:
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
			print("--- %s seconds ---" % str((time.time() - start_time)/index*(totalNum-index)))
			if index>200:
				self.saveToMongoDB( self.generateResult(dateMap, startTs, endTs) )
				return

