from pyswmm import Simulation, Nodes, Links, Subcatchments
import networkx as nx
import FileSettings

import time
global zero_time
zero_time = time.time()

global network, subnetwork
network = nx.DiGraph()
subnetwork = nx.DiGraph()


def create_network(inputfilename=FileSettings.settingsdict['inputfilename']):
    """ This function creates the system-wide NetworkX DiGraph that contains every node and connection.

    :param inputfilename:
    :return:
    """
    global sim
    linklist = []
    with Simulation(inputfilename) as sim:
        for sub in Subcatchments(sim):
            network.add_node(sub.subcatchmentid)
        for nodes in Nodes(sim):
            network.add_node(nodes.nodeid)
        for link in Links(sim):
            linklist.append(link.connections)
        network.add_edges_from(linklist)
        for sub in Subcatchments(sim):
            network.add_edge(sub.subcatchmentid, sub.connection[1])
    return


def subnetwork_delineation(root=FileSettings.settingsdict['root']):
    """ This function traverses the system-wide DiGraph and clips out only the nodes that are 'upstream' of the "root".
    It does this by calling predecessor() on the root, which returns a list of the upstream neighbors.  The function is
    then called recursively on this list until the end of every branch is searched.  This search is often redundant and
    so inefficient, but it is exhaustive and flexible due to the fact that graph object don't add duplicate elements.

    :param root:
    :return:
    """
    subnetwork.add_node(root)
    predecessorlist = list(network.predecessors(root))
    if predecessorlist == []:
        return
    else:
        for i in predecessorlist:
            subnetwork.add_node(i)
            subnetwork_delineation(i)
    return


def subnetwork_subcatchments(inputfilename=FileSettings.settingsdict['inputfilename']):
    """ This function searches the clipped DiGraph from subnetwork_delineation() and compares it to the "subcatchments"
    that are read by PySWMM.  This removes "junctions" and only consideres "subcatchment" names that are upstream of the
    "root" node.  This function is the only one that is actually called, as it itself calls the other create_network()
    subnetwork_delineateion() functions.

    :param inputfilename:
    :return list_of_subcatchments: List of strings containing the names of the subcatchments that fall into the scope of
    the calibration problem.  This variable is used by many other functions to identify the parts of the input file to
    write to.
    """
    global list_of_subcatchments
    list_of_subcatchments = []
    create_network(inputfilename)
    subnetwork_delineation()
    with Simulation(inputfilename) as sim:
        for subcatchment in Subcatchments(sim):
            subcatchmentname = subcatchment.subcatchmentid
            for subnode in subnetwork:
                if subnode == subcatchmentname:
                    list_of_subcatchments.append(subcatchmentname)
    return list_of_subcatchments


subnetwork_subcatchments()