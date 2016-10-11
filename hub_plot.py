"""Script to plot Hubway station data"""

import json
import requests
import numpy as np
import matplotlib.pyplot as plt


def get_station_info():
    """Gets the station info and returns it as a dict."""
    station_info = requests.get('https://api-core.thehubway.com/gbfs/en/station_information.json')
    station_info = station_info.json()
    return station_info

def get_station_occupancy_array():
    """Gets how full the stations are over time"""
    # we want: station number as row, timestamp at column
    time_interval = get_time_interval()
    time_interval = time_interval[1] - time_interval[0]
    time_interval = int(time_interval/10) + 1
    station_occupancy_array = np.zeros((1, time_interval))
    # cumulative_size = 0
    # print("Shape of master:", station_occupancy_array.shape)
    for station_number in range(1, 219):
        station_occupancy_array = np.vstack((station_occupancy_array, get_single_station_occupancy(station_number, time_interval)))
        # new_station_occupancy_array = get_single_station_occupancy(station_number, time_interval)
        # cumulative_size += new_station_occupancy_array.nbytes
    # print("Size of final array would be this many bytes:", cumulative_size)
    return station_occupancy_array

def get_single_station_occupancy(station_number, array_length):
    """Gets how full one station is over time"""
    file_name = 'data/' + str(station_number) + '.txt'
    single_station_occupancy_array = np.full((1, array_length), 2)
    time_interval = get_time_interval()
    line_counter = 1
    try:
        with open(file_name, 'r') as readfile:
            firstline = readfile.readline()
            for next_line in readfile:
                line = json.loads(next_line)
                index = int(line['l_r']) - time_interval[0]
                index = int(index/10)
                if (line['n_b_a'] + line['n_d_a']) == 0:
                    value = 0
                else:
                    value = line['n_b_a'] / (line['n_b_a'] + line['n_d_a'])
                if (index < 0):
                    index = 0
                # print("Line, index, value:", line_counter, index, value)
                single_station_occupancy_array[0][index] = value
                line_counter += 1
    except FileNotFoundError:
        pass
    for index in range(len(single_station_occupancy_array)):
        if single_station_occupancy_array[0][index] == 2:
            single_station_occupancy_array[0][index] = single_station_occupancy_array[0][index-1]
    print("Returned data for station:", station_number, "\n")
    return single_station_occupancy_array

def get_time_interval():
    """Function to get the time interval where data was collected from
    last_updated.txt"""
    with open('last_updated.txt', 'rb') as readfile:
        empty_line = readfile.readline()
        first_line = readfile.readline()
        readfile.seek(-2, 2)
        while readfile.read(1) != b'\n':
            readfile.seek(-2, 1)
        last_line = readfile.readline()
    return (int(first_line.decode("utf-8")), int(last_line.decode("utf-8")))

def parse_station_coordinates(station_info):
    """Takes the station info and returns a list of [id, lat, lon] for each
    station"""
    station_coords = [[],[],[]]
    for station in station_info['data']['stations']:
        station_coords[0].append(station['station_id'])
        station_coords[1].append(station['lat'])
        station_coords[2].append(station['lon'])
    if len(station_coords[0]) == len(station_coords[1]):
        if len(station_coords[0]) == len(station_coords[2]):
            return station_coords
    else:
        return None

def plot_station_locations(station_coords):
    """Takes a list of station coordinates and plots it"""
    plt.figure()
    plt.scatter(station_coords[1], station_coords[2])
    plt.show()

if __name__ == "__main__":
    # station_info = get_station_info()
    # station_coords = parse_station_coordinates(station_info)
    # plot_station_locations(station_coords)
    station_occupancy_array = get_station_occupancy_array()
    print("Shape of final:", station_occupancy_array.shape)
