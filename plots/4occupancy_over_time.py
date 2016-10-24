"""Script to plot Hubway station data"""

import json
import time
import requests
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def get_station_info():
    """Gets the station info and returns it as a dict."""
    station_info = requests.get('https://api-core.thehubway.com/gbfs/en/station_information.json')
    station_info = station_info.json()
    return station_info


def parse_station_coordinates(station_info):
    """Takes the station info and returns a list of [id, lat, lon] for each
    station"""
    station_coords = [[], [], []]
    for station in station_info['data']['stations']:
        station_coords[0].append(station['station_id'])
        station_coords[1].append(station['lat'])
        station_coords[2].append(station['lon'])
    if len(station_coords[0]) == len(station_coords[1]):
        if len(station_coords[0]) == len(station_coords[2]):
            return station_coords
    else:
        return None


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


def get_time_interval():
    """Function to get the time interval where data was collected from
    last_updated.txt"""
    with open('../last_updated.txt', 'rb') as readfile:
        readfile.readline()
        first_line = readfile.readline()
        readfile.seek(-2, 2)
        while readfile.read(1) != b'\n':
            readfile.seek(-2, 1)
        last_line = readfile.readline()
    return (int(first_line.decode("utf-8")), int(last_line.decode("utf-8")))


def get_single_station_occupancy(station_number, array_length):
    """Gets how full one station is over time"""
    file_name = '../data/' + str(station_number) + '.txt'
    single_station_occupancy_array = np.full((1, array_length), 2)
    time_interval = get_time_interval()
    line_counter = 1
    try:
        with open(file_name, 'r') as readfile:
            readfile.readline()
            for next_line in readfile:
                line = json.loads(next_line)
                index = int(line['l_r']) - time_interval[0]
                index = int(index/10)
                if line['n_b_a'] + line['n_d_a'] == 0:
                    value = 0
                else:
                    value = line['n_b_a'] / (line['n_b_a'] + line['n_d_a'])
                if (index < 0):
                    index = 0
                single_station_occupancy_array[0][index] = value
                line_counter += 1
    except FileNotFoundError:
        pass
    print("Returned data for station:", station_number, "\n")
    return single_station_occupancy_array

def get_station_hourly_average(station_occupancy_array):
    """Gets the averages for all the stations and returns an array"""
    averages_array = np.full((1, int(station_occupancy_array.shape[1]/360+1)), 0)
    for station_num in range(1, 219):
        averages_array = np.vstack((averages_array, get_single_station_hourly_average(station_occupancy_array, station_num)))
    return averages_array

def get_single_station_hourly_average(station_occupancy_array, station_num):
    """Gets the average for one station and returns an array"""
    end = int(station_occupancy_array.shape[1] / 360 + 1)
    begin = 0
    average_array = np.full((1, end), 0)
    average = 0
    last_item = 0
    while begin < end-1:
        temp = station_occupancy_array[station_num][begin*360: begin*360+360]
        for item in temp:
            if item <= 1:
                average += item
                last_item = item
            else:
                average += last_item
        average_array[0][begin] = average/360
        # print("Station, Hour, Average", station_num, begin, average/360)
        begin += 1
        average = 0
    return average_array

def plot_stations_hourly_average(station_averages, station_coords, time_interval):
    """Creates a bunch of plots based on the hourly station average"""
    colorline = cm.rainbow(np.linspace(0, 1, 2001))
    for index in range(station_averages.shape[1]):
        plt.figure()
        average_slice = station_averages[:, index]
        station_colormap = [colorline[int(2000*x)] for x in average_slice]
        average_slice = [600 * x for x in average_slice]
        plt.scatter(station_coords[2], station_coords[1], s=average_slice, c=station_colormap)
        plt.title(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time_interval[0]+3600*index)))
        plt.xlim(-71.20, -70.95)
        plt.ylim(42.25, 42.45)
        plt.savefig('../diagrams/4_'+str(index)+'.png')
        plt.close()
        print("Generated figure:", index)


if __name__ == "__main__":
    # To plot station data via GPS coordinates and station occupancy
    time_interval = get_time_interval()
    station_info = get_station_info()
    station_coords = parse_station_coordinates(station_info)
    station_occupancy_array = get_station_occupancy_array()
    station_averages = get_station_hourly_average(station_occupancy_array)
    plot_stations_hourly_average(station_averages, station_coords, time_interval)
