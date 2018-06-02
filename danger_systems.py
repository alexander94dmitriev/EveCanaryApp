# Step 1: Get the list of adjacent systems
# Step 2: Get the list of recent kills and see if they have happened in those systems.
#   Alert user if there is potential danger
#   Alert user if there is NO potential danger
# Step 3: Continue checking for recent kills (and make comparisons)
"""
    This code is released under an MIT license
"""
from network_local import build_graph_wrapper
from zkillboard_info import get_Zkillboard_data
import time
import winsound

from os import path
import json

# Creates the list of adjacent systems, including base system
def gather_systems(location, jumps):
    systems = list(build_graph_wrapper(location, jumps))
    systems = sorted(systems)
    return systems


# Searches all systems to see if there was hostile activity recently
def check_for_danger(systems_to_check, time_range):
    systems = get_Zkillboard_data(systems_to_check, time_range)
    systems = sorted(systems)

    if systems:
        report_danger(systems)

#Go into "refresh mode", where every X seconds, zkillboard is queried again.
def refresh_scan(systems_to_check, rate, time_range):
    #threading.Timer(rate, refresh_scan, [systems_to_check, rate, time_range]).start()
    check_for_danger(systems_to_check, time_range)

def scan_systems(char_location = '30001005', num_jumps = 2, refresh_rate = 60., initial_time = 240, recur_time = 1):

    #initial check
    adj_systems = gather_systems(char_location, num_jumps)
    check_for_danger(adj_systems, initial_time)

    print("Onto recurrence: \n")

    time.sleep(10)

    #recurring checks
    refresh_scan(adj_systems, refresh_rate, recur_time)

def find_danger_systems(char_location = '30001005', num_jumps = 2, hours=4):

    # Creates the list of adjacent systems, including base system
    systems = list(build_graph_wrapper(char_location, num_jumps))
    systems = sorted(systems)
    systems = list(split_list_on_chunks(systems))

    # Searches all systems to see if there was hostile activity recently
    danger_systems = []

    for system in systems:
        check_system = get_Zkillboard_data(system, hours)
        if check_system:
            danger_systems.append(check_system)

    return get_system_names(danger_systems)

def split_list_on_chunks(list, num=10):
    for i in range(0, len(list), num):
        yield list[i:i + num]

def get_system_names(systems):
    system_names = []
    with open(path.join(path.dirname(path.abspath(__file__)), 'eve-map.json')) as f:
        data = json.load(f)
        for system in systems:
            system_names.append(data['systems'][str(system)]['name'])

    if system_names:
        winsound.PlaySound("beepsound.wav", winsound.SND_FILENAME)
        winsound.PlaySound("beepsound.wav", winsound.SND_FILENAME)
        winsound.PlaySound("beepsound.wav", winsound.SND_FILENAME)

    return system_names