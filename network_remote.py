import networkx as nx
from esipy import App
from esipy import EsiClient
import config

graph = nx.DiGraph()
queue = list()# LIFO queue
esiapp = App.create(config.ESI_SWAGGER_JSON)
# init the client
esiclient = EsiClient(
    cache=None,
    headers={'User-Agent': config.ESI_USER_AGENT}
)

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
    char_system_info_req = esiapp.op['get_universe_systems_system_id'](system_id=current_location)
    char_system_info = esiclient.request(char_system_info_req).data
    system_stargates = char_system_info['stargates']

    for stargate in system_stargates:
        char_system_stargate = esiapp.op['get_universe_stargates_stargate_id'](stargate_id=stargate)
        char_system_stargate = esiclient.request(char_system_stargate).data
        stargate_destination = str(char_system_stargate['destination']['system_id'])
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

def build_graph_wrapper(char_location='30002267', num_of_jumps=1):
    # Current location of Kaleb Plaude
    queue.append(char_location)
    graph.add_node(char_location)
    build_graph(char_location, char_location, num_of_jumps)

    # Gives you graph max depth
    depth = nx.shortest_path_length(graph, char_location)
    longest_depth = max(depth.values())
    print("Total depth: {}".format(longest_depth))

    return graph

build_graph_wrapper()
#nx.draw(build_graph_wrapper(), with_labels=True)
#plt.show()