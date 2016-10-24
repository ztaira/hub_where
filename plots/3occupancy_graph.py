"""Script to plot Hubway station occupancy data"""

import matplotlib.pyplot as plt

def plot_occupancy(occupancy_data):
    """Plots station occupancy"""
    fig, ax = plt.subplots()
    ax.bar(occupancy_data[0], occupancy_data[1], width=1, color='b')
    plt.ylim([0, 1])
    plt.title("Average Occupancy by Station Number")
    plt.xlabel("Station Number")
    plt.ylabel("Average Occupancy (bikes / (bikes + docks))")
    plt.xlim(0, 225)
    plt.savefig('../diagrams/3occupancy_graph.pdf')
    plt.show()


def get_occupancy_data():
    """Gets the occupancy data"""
    # first index is list of station numbers
    # second index is list of average occupancies
    occupancy_data = [[], []]
    with open('average_occupancies.txt', 'r') as readfile:
        for line in readfile:
            newline = line.split(':')
            occupancy_data[0].append(int(newline[0]))
            occupancy_data[1].append(float(newline[1]))
    return occupancy_data

if __name__ == "__main__":
    occupancy_data = get_occupancy_data()
    plot_occupancy(occupancy_data)
