"""Script to plot data by GPS coordinates and log size"""

import requests
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt

def get_station_info():
    """Gets the station info and returns it as a dict."""
    station_info = requests.get('https://api-core.thehubway.com/gbfs/en/station_information.json')
    station_info = station_info.json()
    return station_info


def get_file_length_array():
    """Gets an array containing all the station lengths"""
    file_length_array = []
    for station_number in range(219):
        file_length_array.append(get_file_length(station_number))
    file_length_array = [x for x in file_length_array if x != -1]
    return file_length_array


def get_file_length(station_number):
    """Gets the length of a station's data file"""
    file_name = '../data/' + str(station_number) + '.txt'
    line_number = 0
    try:
        with open(file_name, 'r') as readfile:
            for line in readfile:
                line_number += 1
    except FileNotFoundError:
        line_number = -1
    return line_number


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


def plot_station_locations_and_activity(station_coords, station_activity):
    """Takes a list of station coordinates and plots it"""
    # for size
    plt.figure(figsize=(16, 12), dpi=120)
    station_activity = [0.7*x for x in station_activity]
    plt.scatter(station_coords[2], station_coords[1], s=station_activity)
    plt.title("Hubway Stations by Activity Level (Size)")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.ylim(42.25, 42.45)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.savefig('../diagrams/1activity_by_size.png')

    # for color
    plt.figure(figsize=(16, 12), dpi=120)
    colorline = cm.rainbow(np.linspace(0, 1, max(station_activity)+1))
    station_colormap = [colorline[x] for x in station_activity]
    plt.scatter(station_coords[2], station_coords[1], s=350, c=station_colormap)
    plt.title("Hubway Stations by Activity Level (Color)")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.ylim(42.25, 42.45)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.savefig('../diagrams/1activity_by_color.png')

    # for size and color:
    plt.figure(figsize=(16, 12), dpi=120)
    plt.scatter(station_coords[2], station_coords[1], s=station_activity, c=station_colormap)
    plt.title("Hubway Stations by Activity Level (Color and Size)")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.ylim(42.25, 42.45)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.savefig('../diagrams/1activity_by_color_and_size.png')

    # plt.show()


if __name__ == "__main__":
    # To plot station data via GPS coordinates and station activity
    station_info = get_station_info()
    station_activity = get_file_length_array()
    station_coords = parse_station_coordinates(station_info)
    plot_station_locations_and_activity(station_coords, station_activity)
