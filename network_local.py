import networkx as nx
import matplotlib.pyplot as plt
import json
from os import path

graph = nx.DiGraph()
queue = list()# LIFO queue

data = None

with open(path.join(path.dirname(path.abspath(__file__)),'eve-map.json')) as f:
    data = json.load(f)

# This function gets all of the adjacent systems withing given max_depth (# of jumps) starting with current_location
# Go through all stargates in the system and get their destinations. Add all of them in a queue
# When done looping through stargates, pop current location node, you done here
# Recursively call function to work with next queue element in LIFO manner
# The function should stop when you start going out of given range
def build_graph(root, current_location, max_depth):

    if len(queue) == 0:
        return
    longest_depth = nx.dag_longest_path_length(graph, root)
    if longest_depth > max_depth:
        path = nx.dag_longest_path(graph, root)
        graph.remove_node(path[-1])
        return
    system_stargates = []
    for stargate in data['stargates']:
        curr_stargate = data['stargates'][stargate]
        if curr_stargate['system_id'] == int(current_location):
            system_stargates.append(curr_stargate)

    for stargate in system_stargates:
        stargate_destination = str(stargate['destination']['system_id'])
        nodes = list(graph.nodes)

        # We want to avoid cycles if we want to use dag_longest_path_length, so we want to work with destination that
        # are not in the graph yet
        if(stargate_destination not in nodes):
            print('{} -> {}'.format(current_location, stargate_destination))
            graph.add_edge(current_location, stargate_destination)

        longest_depth = nx.dag_longest_path_length(graph, root)
        if longest_depth > max_depth:
            path = nx.dag_longest_path(graph, root)
            graph.remove_node(path[-1])
            return
        else:
            queue.append(stargate_destination)

    queue.pop(0)

    longest_depth = nx.dag_longest_path_length(graph, root)
    print(longest_depth)
    if longest_depth > max_depth:
        path = nx.dag_longest_path(graph, root)
        graph.remove_node(path[-1])
        return

    stargate_destination = queue[0]
    build_graph(root, stargate_destination, max_depth)

def build_graph_wrapper(char_location='30002267', num_of_jumps=6):
    # Current location of Kaleb Plaude
    queue.append(char_location)
    graph.add_node(char_location)
    build_graph(char_location, char_location, num_of_jumps)

    # Gives you graph max depth
    depth = nx.shortest_path_length(graph, char_location)
    longest_depth = max(depth.values())
    print("Total depth: {}".format(longest_depth))

    return graph

#build_graph_wrapper()
#nx.draw(build_graph_wrapper(), with_labels=True)
#plt.show()
