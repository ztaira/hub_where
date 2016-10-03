"""Script to collect data on Hubway stations."""

import time
import json
import requests


def setup():
    """If last_updated.txt does not exist, create the files that will be
    used to store Hubway station data.

    This makes sure that the text files exist, so writing to them
    later doesn't throw any errors."""
    try:
        with open('last_updated.txt', 'r') as readfile:
            pass
    except:
        station_status = get_station_status()
        with open('last_updated.txt', 'a') as workfile:
            workfile.write('\n')
            workfile.write(str(int(station_status['last_updated'])))
        for station in station_status['data']['stations']:
            file_name = 'data/' + station['station_id'] + '.txt'
            with open(file_name, 'a') as workfile:
                workfile.write('\n')
                station = shorten_dict(station)
                workfile.write(json.dumps(station))


def get_station_status():
    """Gets the station status via Hubway's API and returns it as a dict."""
    station_status = requests.get('https://api-core.thehubway.com/gbfs/en/station_status.json')
    station_status = station_status.json()
    return station_status


def update_station_logs(station_status):
    """Updates the station logs and last_updated.txt"""
    # if the file's last updated time < the station's last updated time:
    # log the station's last updated time to file
    if int(get_last_line('last_updated.txt')) < int(station_status['last_updated']):
        with open('last_updated.txt', 'a') as workfile:
            workfile.write('\n')
            workfile.write(str(int(station_status['last_updated'])))
    # for every station in station_status:
    # if the log's last_reported time < the station's last reported time:
    # log the station's information to file
    for station in station_status['data']['stations']:
        file_name = 'data/' + station['station_id'] + '.txt'
        last_line = json.loads(get_last_line(file_name))
        if last_line['l_r'] < station['last_reported']:
            with open(file_name, 'a') as workfile:
                workfile.write('\n')
                station = shorten_dict(station)
                workfile.write(json.dumps(station))


def get_last_line(file_name):
    """Function to return the last line of a given text file as a string."""
    with open(file_name, 'rb') as readfile:
        readfile.seek(-2, 2)
        while readfile.read(1) != b'\n':
            readfile.seek(-2, 1)
        last_line = readfile.readline()
    return last_line.decode("utf-8")


def shorten_dict(station):
    """Function to shorten a station dict's keys so that it takes up less space."""
    station['s_i'] = station.pop('station_id', None)
    station['e_h_a_k'] = station.pop('eightd_has_available_keys', None)
    station['i_ret'] = station.pop('is_returning', None)
    station['n_b_d'] = station.pop('num_bikes_disabled', None)
    station['n_d_d'] = station.pop('num_docks_disabled', None)
    station['l_r'] = station.pop('last_reported', None)
    station['i_i'] = station.pop('is_installed', None)
    station['n_b_a'] = station.pop('num_bikes_available', None)
    station['n_d_a'] = station.pop('num_docks_available', None)
    station['i_ren'] = station.pop('is_renting', None)
    return station

if __name__ == "__main__":
    print("Starting logging!")
    setup()
    while True:
        if time.time() % 60 == 0:
            print(int(time.time()))
            update_station_logs(get_station_status())
