from threading import Thread
import time
import datetime
import json
import requests
import csv

# Create keys.py in same directory and include API keys
from keys import METRA_USER, METRA_PASS, WEATHER_KEY

import logging as log # Setup logging
log.basicConfig(filename='data/data_collection.log', 
                filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', 
                level=log.INFO)

# Global API URLs
TRIPUPDATES_URL = "https://gtfsapi.metrarail.com/gtfs/tripUpdates"
ALERTS_URL = "https://gtfsapi.metrarail.com/gtfs/alerts"
WEATHER_URL = lambda lat,lon: "https://api.openweathermap.org/data/2.5/weather \
                          ?lat="+str(lat)+"&lon="+str(lon)+"&appid="+WEATHER_KEY

def RequestData(URL, User=None, Pass=None):
	return json.loads(requests.get(URL, 
	                               auth=(User, Pass) if User and Pass else None).text)

def CollectAlerts():
	try:
		with open("data/alert.csv","a", newline='') as alerts: # open/close file
			alertsWriter = csv.writer(alerts) # setup writer
			while True:
				# setup variables
				alertsRawData = None
				attempts = 0
				while attempts < 10: # try to connect
					try: 
						alertsRawData = RequestData(ALERTS_URL, METRA_USER, METRA_PASS)
					except requests.exceptions.RequestException as e: 
						# if requests fail after 10 trys skip, try in 30 min
						attempts += 1
						log.error('Operation failed: \
                                   %s with %d attempts remaining' \
						          % (e, 10-attempts))
					else: break # data collected break request loop

				try:
					if not alertsRawData: 
						raise ValueError("Data collection from the server failed")

					# setup variables
					affectedRoutes = []
					alertsData = []

					for alert in range(len(alertsRawData)): 
						# filter data and write to csv
						for routes in alertsRawData[alert]['alert']['informed_entity']:
							affectedRoutes += [routes['route_id']]
							try:
								alertsData = [time.time(),
								              datetime.datetime.now(),
								              alertsRawData[alert]['id'],
								              affectedRoutes,
								              alertsRawData[alert]['alert']['active_period'][0]['start']['low'],
								              alertsRawData[alert]['alert']['active_period'][0]['end']['low'],
								              alertsRawData[alert]['alert']['cause'], 
								              alertsRawData[alert]['alert']['effect'], 
								              alertsRawData[alert]['alert']['description_text']['translation'][0]['text']]
							except KeyError as e:
								log.error('Operation failed: %s , \
                                           Alert data missing key' % e)
								tripData = None
							else:
								alertsWriter.writerow(alertsData)

								logData_lst = [str(data) for data in alertsData]
								logData = "".join(logData_lst)
								log.info("Alert Data: " + logData)
				except ValueError as e: 
					log.error('Operation failed: %s' % e)
				finally: 
					time.sleep(1800) # check for new alerts after 30 mins

	except IOError as e: 
		log.error('Operation failed: %s' % e)
		raise IOError(e)

def CollectData():
	try:
		with open("data/trip.csv","a", newline='') as trip: # open/close file
			tripWriter = csv.writer(trip) # setup writer
			while True:
				# setup variables
				tripData = [] 
				weatherData = []
				try:
					tripRawData = RequestData(TRIPUPDATES_URL, 
					                          METRA_USER, 
					                          METRA_PASS) # request data

					# keep collected time the same for each route
					collectedTimeFormatted = datetime.datetime.now()
					collectedTime = time.time()

					for trip in range(len(tripRawData)): # filter/write data to csv
						try:
							tripData = [collectedTime,
							            collectedTimeFormatted,
							            tripRawData[trip]['id'],
							            tripRawData[trip]['trip_update']['trip']['route_id'],
							            tripRawData[trip]['trip_update']['position']['vehicle']['vehicle']['id'],
							            tripRawData[trip]['trip_update']['position']['vehicle']['vehicle']['label'],
							            tripRawData[trip]['trip_update']['stop_time_update'][0]['arrival']['delay'], 
							            tripRawData[trip]['trip_update']['position']['vehicle']['position']['latitude'], 
							            tripRawData[trip]['trip_update']['position']['vehicle']['position']['longitude']]
						except KeyError as e:
							log.error('Operation failed: %s , \
                                       Trip data missing key' % e)
							tripData = None
						else:
							logData_lst = [str(data) for data in tripData]
							logData = "".join(logData_lst)
							log.info("Trip Data: " + logData)

						try:
							weatherRawData = RequestData(WEATHER_URL(tripRawData[trip]['trip_update']['position'] \
							                                         ['vehicle']['position'] \
							                                         ['latitude'],
							                                         tripRawData[trip]['trip_update']['position'] \
							                                         ['vehicle']['position'] \
							                                         ['longitude']))                            
							weatherData = [weatherRawData['weather'], 
							               weatherRawData['main']['temp'], 
							               weatherRawData['main']['temp_min'], 
							               weatherRawData['main']['temp_max'], 
							               weatherRawData['visibility'],
							               weatherRawData['wind']['speed']]
						except KeyError as e:
							log.error('Operation failed: %s , \
                                       Weather data missing key' % e)
							weatherData = []
						else:
							logData_lst = [str(data) for data in weatherData]
							logData = "".join(logData_lst)
							log.info("Weather Data: " + logData)

						if tripData is not None:
							fullData = tripData + weatherData
							tripWriter.writerow(fullData)

				except requests.exceptions.RequestException as e: 
					log.error('Operation failed: %s' % e)
				finally: 
					time.sleep(30)          
	except IOError as e: 
		log.error('Operation failed: %s' % e)
		raise IOError(e)

if __name__ == "__main__":
	mainDataThread = Thread(name='Main Data Collection', target=CollectData)
	alertsDataThread = Thread(name='Alert Data Collection', target=CollectAlerts)

	mainDataThread.setDaemon(True)
	alertsDataThread.setDaemon(True)

	mainDataThread.start()
	alertsDataThread.start()

	while True:
		pass # allow threads to continue as daemons
