"""Script to plot Hubway station data"""

import json
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


def get_station_averages(station_occupancy_array):
    """Gets how full the stations are on average"""
    average_list = []
    counter = 0
    for station in station_occupancy_array:
        cumulative_total = 0
        last_item = 0
        for item in station:
            if item <= 1:
                cumulative_total += item
                last_item = item
            else:
                cumulative_total += last_item
        average = cumulative_total / len(station)
        average_list.append(average)
        counter += 1
        print("Got the average for another station", counter)
    average_list = [x for x in average_list if x != 0]
    return average_list


def plot_station_locations_and_occupancy(station_coords, station_occupancies):
    """Takes a list of station coordinates and plots it"""

    # for size
    plt.figure(figsize=(16, 12), dpi=120)
    station_occupancies_scaled = [1000*x for x in station_occupancies]
    plt.scatter(station_coords[2], station_coords[1], s=station_occupancies_scaled)
    plt.title("Hubway Stations by Average Occupancy (Size)")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.ylim(42.25, 42.45)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.savefig('../diagrams/2occupancy_by_size.png')

    # for color:
    plt.figure(figsize=(16, 12), dpi=120)
    colorline = cm.rainbow(np.linspace(0, 1, 1001))
    station_colormap = [colorline[int(x)] for x in station_occupancies_scaled]
    plt.scatter(station_coords[2], station_coords[1], s=400, c=station_colormap)
    plt.title("Hubway Stations by Average Occupancy (Color)")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.ylim(42.25, 42.45)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.savefig('../diagrams/2occupancy_by_color.png')

    # for size and color
    plt.figure(figsize=(16, 12), dpi=120)
    plt.scatter(station_coords[2], station_coords[1], s=station_occupancies_scaled, c=station_colormap)
    plt.title("Hubway Stations by Average Occupancy (Size and Color)")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.ylim(42.25, 42.45)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.savefig('../diagrams/2occupancy_by_color_and_size.png')

    # plt.show()


if __name__ == "__main__":
    # To plot station data via GPS coordinates and station occupancy
    station_info = get_station_info()
    station_coords = parse_station_coordinates(station_info)
    station_occupancy_array = get_station_occupancy_array()
    station_occupancies = get_station_averages(station_occupancy_array)
    with open('average_occupancies.txt', 'w') as writefile:
        for item in range(len(station_occupancies)):
            writefile.write(str(station_coords[0][item]) + ":" + str(station_occupancies[item]) + '\n')
    plot_station_locations_and_occupancy(station_coords, station_occupancies)
