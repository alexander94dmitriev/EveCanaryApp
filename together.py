#Step 1: Get the list of adjacent systems
#Step 2: Get the list of recent kills and see if they have happened in those systems.
#   Alert user if there is potential danger
#   Alert user if there is NO potential danger
#Step 3: Continue checking for recent kills (and make comparisons)

from network_test import build_graph
from zkillboard_info import get_Zkillboard_data

char_location = '30001005'
num_jumps = 2
adjLocs = []
system_list = []

#Creates the list of adjacent systems, including base system
adjLocs.append(char_location)
build_graph(char_location, char_location, num_jumps, adjLocs)

#Searches all systems to see if there was hostile activity recently
dangerSystems = []

for item in adjLocs:
    #dangerSystems.append(get_Zkillboard_data(item, 24, dangerSystems))
    get_Zkillboard_data(item, 24, dangerSystems)

#zkillInfo = get_Zkillboard_data(char_location, 24, system_list)



print("Testing.\n")

