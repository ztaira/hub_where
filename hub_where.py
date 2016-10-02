import time
import pprint
import json
import requests
import urllib.request

# get the station information
# station_info = requests.get('https://api-core.thehubway.com/gbfs/en/station_information.json')
# station_info = station_info.json()

def setup():
    try:
        with open('last_updated.txt', 'r') as readfile:
            pass
    except:
        station_status = get_station_status()
        with open('last_updated.txt', 'a') as workfile:
            workfile.write(str(station_status['last_updated']))
        for station in station_status['data']['stations']:
            file_name = station['station_id'] + '.txt'
            with open(file_name, 'a') as workfile:
                workfile.write(json.dumps(station))

def get_station_status():
    station_status = requests.get('https://api-core.thehubway.com/gbfs/en/station_status.json')
    station_status = station_status.json()
    return station_status

def update_station_logs(station_status):
    # firstly, log to the last updated file
    # then, for every station in the station_status dict passed in:
    # if the last reported time in the file is less than the time in the dict:
    # write the dict to the file
    # otherwise do nothing
    with open('last_updated.txt', 'a') as workfile:
        workfile.write(str(station_status['last_updated']))
    for station in station_status['data']['stations']:
        print(station['station_id'])
        file_name = station['station_id'] + '.txt'
        last_line = json.loads(get_last_line(file_name))
        if last_line['last_reported'] < station['last_reported']:
            with open(file_name, 'a') as workfile:
                workfile.write(json.dumps(station))

def get_last_line(file_name):
    with open(file_name, 'rb') as readfile:
        readfile.seek(-2, 2)
        while readfile.read(1) != b'\n':
            readfile.seek(-2, 1)
        last_line = readfile.readline()
    return last_line

if __name__ == "__main__":
    print("Starting logging!")
    setup()
    while True:
        if time.time() % 60 == 0:
            print(time.time())
            update_station_logs(get_station_status())
