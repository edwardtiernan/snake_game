from pyswmm import Simulation, Nodes, Links, Subcatchments
import networkx as nx
import FileSettings

import time
start_time = time.time()

global network, subnetwork
network = nx.DiGraph()
subnetwork = nx.DiGraph()
def createnetwork(inputfilename=FileSettings.settingsdict['inputfilename']):
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
createnetwork()


def subnetworkdelineation(root=FileSettings.settingsdict['root']):
    subnetwork.add_node(root)
    predecessorlist = list(network.predecessors(root))
    if predecessorlist == []:
        return
    else:
        for i in predecessorlist:
            subnetwork.add_node(i)
            subnetworkdelineation(i)
    return


def subnetwork_subcatchments(inputfilename=FileSettings.settingsdict['inputfilename'], root=FileSettings.settingsdict['root']):
    global list_of_subcatchments
    list_of_subcatchments = []
    createnetwork(inputfilename)
    subnetworkdelineation()
    with Simulation(inputfilename) as sim:
        for subcatchment in Subcatchments(sim):
            subcatchmentname = subcatchment.subcatchmentid
            for subnode in subnetwork:
                if subnode == subcatchmentname:
                    list_of_subcatchments.append(subcatchmentname)
    return(list_of_subcatchments)

subnetwork_subcatchments()





