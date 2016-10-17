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
    # we want: station number as row, timestamp at column, number of bikes as
        # content
    # For example, station_occupancy_array[station_number][timestamp] = 12/15 bikes
    # I also left debugging comments in here because the array
        # is uncomfortably large
    time_interval = get_time_interval()
    time_interval = time_interval[1] - time_interval[0]
    time_interval = int(time_interval/10) + 1
    station_occupancy_array = np.full((1, time_interval), 2)
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
                single_station_occupancy_array[0][index] = value
                line_counter += 1
    except FileNotFoundError:
        pass
    for index in range(len(single_station_occupancy_array)):
        if single_station_occupancy_array[0][index] == 2:
            single_station_occupancy_array[0][index] = single_station_occupancy_array[0][index-1]
    print("Returned data for station:", station_number, "\n")
    return single_station_occupancy_array

def get_file_length_array():
    """Gets an array containing all the station lengths"""
    file_length_array = []
    for station_number in range(219):
        file_length_array.append(get_file_length(station_number))
    for item in reversed(file_length_array):
        if item == -1:
            file_length_array.pop(item)
    return file_length_array


def get_file_length(station_number):
    """Gets the length of a station's data file"""
    file_name = 'data/' + str(station_number) + '.txt'
    line_number = 0
    try:
        with open(file_name, 'r') as readfile:
            for line in readfile:
                line_number += 1
    except FileNotFoundError:
        line_number = -1
    return line_number

def get_station_averages(station_occupancy_array):
    """Gets how full the stations are on average"""
    average_list = []
    cumulative_total = 0
    num_entries = 0
    for station in station_occupancy array:
        for item in station:
            print(item)
            if item <= 1:
                cumulative_total += item
                num_entries += 1
            else:
                cumulative_total += 0
        average = cumulative_total / num_entries
        cumulative_total = 0
        num_entries = 0
        average_list.append(average)
    for item in reversed(average_list):
        if item == -1:
            average_list.pop(item)
    return average_list

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

def plot_station_locations_and_activity(station_coords, station_activity):
    """Takes a list of station coordinates and plots it"""
    plt.figure()
    plt.scatter(station_coords[2], station_coords[1], s=station_activity)
    plt.title("Hubway Stations by GPS Coordinates and Activity Level")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

if __name__ == "__main__":
    # To plot station data via GPS coordinates and station activity
    station_info = get_station_info()
    station_activity = get_file_length_array()
    station_coords = parse_station_coordinates(station_info)
    for item in station_coords:
        print(item)
    plot_station_locations_and_activity(station_coords, station_activity)

    station_occupancy_array = get_station_occupancy_array()
    get_station_averages(station_occupancy_array)
