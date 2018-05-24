# Step 1: Get the list of adjacent systems
# Step 2: Get the list of recent kills and see if they have happened in those systems.
#   Alert user if there is potential danger
#   Alert user if there is NO potential danger
# Step 3: Continue checking for recent kills (and make comparisons)

from network_test import build_graph_wrapper
from zkillboard_info import get_Zkillboard_data

char_location = '30001005'
num_jumps = 2

# Creates the list of adjacent systems, including base system

systems = list(build_graph_wrapper(char_location, num_jumps))

# Searches all systems to see if there was hostile activity recently
#systems = list(map(int, systems))
systems = sorted(systems)
#systems = systems.sort(key=int)
dangerSystems = get_Zkillboard_data(systems, 4)

print(dangerSystems)


