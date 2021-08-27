#!/usr/bin/env python
import osmnx as ox
import networkx as nx
import pandas as pd
from vincenty import vincenty
import numpy as np

def getSubnodes(route_map,route):
    """
    Get roughly metre-spaced subnodes along a route
    
    Parameters:
        route_map (graph): graph of walking map.
        
        route (list): list of nodes.

    Returns:
        subnodes (list): list of dictionaries detailing lat,lon and osmid of the containing edge for each subnode
    """
    
    subnodes = []
    
    for i in range(len(route)-1):
        
        # break up each edge into straigt line segments
        if "geometry" in route_map.edges[(route[i],route[i+1],0)]:
            _edge = route_map.edges[(route[i],route[i+1],0)]
            _edge_geometry = _edge["geometry"]
            _joints = [(coord[1],coord[0]) for coord in list(_edge_geometry.coords)]

        
            #_joints = [{"lat":coord[1],"lon":coord[0],"edge_osmid":_edge["osmid"]} for coord in list(_edge_geometry.coords)]
        else:
            _edge = route_map.edges[(route[i],route[i+1],0)]
            _joints = [(route_map.nodes[route[i]]['y'],route_map.nodes[route[i]]['x']), (route_map.nodes[route[i+1]]['y'],route_map.nodes[route[i+1]]['x'])]
        
        if len(_joints) < 2:
            raise TypeError("No joints found!")
        
        for j in range(len(_joints)-1):
            
            # for each straight line segment generate metre-spaced subnodes
            _dist = 1000*vincenty(_joints[j],_joints[j+1])
            _n = int(_dist)
            if _n > 1:
                _edge_subnodes = [{"lat":subnode[0],"lon":subnode[1],"node_osmids":(route[i],route[i+1])} for subnode in np.linspace(_joints[j],_joints[j+1],_n+1)]
            else:
                _edge_subnodes = [{"lat":subnode[0],"lon":subnode[1],"node_osmids":(route[i],route[i+1])} for subnode in [_joints[j],_joints[j+1]]]
                
            # avoid adding duplicate subnodes at the endpoints
            subnodes += list(_edge_subnodes[:-1])
            
    # add the final node separately       
    subnodes.append({"lat":route_map.nodes[route[-1]]['y'],"lon":route_map.nodes[route[-1]]['x'],"node_osmids":(route[i],route[i+1])})
                
                
    return subnodes
