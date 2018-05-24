# Step 1: Get the list of adjacent systems
# Step 2: Get the list of recent kills and see if they have happened in those systems.
#   Alert user if there is potential danger
#   Alert user if there is NO potential danger
# Step 3: Continue checking for recent kills (and make comparisons)

import threading
from network_test import build_graph_wrapper
from zkillboard_info import get_Zkillboard_data


# Creates the list of adjacent systems, including base system
def gather_systems(location, jumps):
    systems = list(build_graph_wrapper(location, jumps))
    systems = sorted(systems)
    return systems


# Searches all systems to see if there was hostile activity recently
def check_for_danger(systems_to_check, time_range):
    systems = get_Zkillboard_data(systems_to_check, time_range)

    if systems:
        report_danger(systems)


#if hostile activity, inform the user (No alert because this is a history search)
def report_danger(systems_to_report):
    print("The following systems are dangerous: \n")
    print(systems_to_report)


#Go into "refresh mode", where every X seconds, zkillboard is queried again.
def refresh_scan(systems_to_check, rate, time_range):
    threading.Timer(rate, refresh_scan).start()
    check_for_danger(systems_to_check, time_range)


#default parameters
char_location = '30001005'
num_jumps = 2
refresh_rate = 15.0
initial_time = 4
recur_time = .016

#initial check
adj_systems = gather_systems(char_location, num_jumps)
check_for_danger(adj_systems, initial_time)

print("Onto recurrence: \n")

#recurring checks
refresh_scan(adj_systems, refresh_rate, recur_time)