#!/usr/bin/env python3
# encoding=utf-8

import os
import lnetatmo
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.exceptions import InfluxDBError
from influxdb_client.client.write_api import SYNCHRONOUS

CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
USERNAME = os.environ['USERNAME']
PASSWORD = os.environ['PASSWORD']
INFLUXDBHOST = os.environ['INFLUXDBHOST']
TOKEN = os.environ['TOKEN']
ORG = os.environ['ORG']
BUCKET = os.environ['BUCKET']

authorization = lnetatmo.ClientAuth(
        clientId=CLIENT_ID,
        clientSecret=CLIENT_SECRET,
        username=USERNAME,
        password=PASSWORD,
        scope='read_station'
        )

weatherData = lnetatmo.WeatherStationData(authorization)

client = InfluxDBClient(url=INFLUXDBHOST, token=TOKEN, org=ORG
write_api = client.write_api(write_options=SYNCHRONOUS)

for station in weatherData.stations:
    station_data = []
    module_data = []
    station_name = weatherData.stations[station]['station_name']
    altitude = weatherData.stations[station]['place']['altitude']
    country= weatherData.stations[station]['place']['country']
    timezone = weatherData.stations[station]['place']['timezone']
    longitude = weatherData.stations[station]['place']['location'][0]
    latitude = weatherData.stations[station]['place']['location'][1]
    for module, moduleData in weatherData.lastData(exclude=3600).items():
        for measurement in ['altitude', 'country', 'longitude', 'latitude', 'timezone']:
            value = eval(measurement)
            if type(value) == int:
                value = float(value)
            station_data.append({
                "measurement": measurement,
                "tags": {
                    "station": station_name,
                    "module": module
                },
                "time": moduleData['When'],
                "fields": {
                    "value": value
                }
            })

        for sensor, value in moduleData.items():
            if sensor.lower() != 'when':
                if type(value) == int:
                    value = float(value)
                module_data.append({
                    "measurement": sensor.lower(),
                    "tags": {
                        "station": station_name,
                        "module": module
                    },
                    "time": moduleData['When'],
                    "fields": {
                        "value": value
                    }
                })


    write_api.write(BUCKET, ORG, station_data, write_precision='s')
    write_api.write(BUCKET, ORG, module_data, write_precision='s')
