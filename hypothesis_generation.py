import sys
import json
import statistics
from centrality import Centrality
from glob import glob

import os.path

def print_path(path):
    print (path)
    
def get_json_string(node_path):
    dta = ''
    try:
        with open(node_path, 'r') as j:
             dta = json.loads(j.read())
    except(IOError):
        print('File was not found:')
        print(node_path)

    return dta
    
def get_graph_json(json_path):
    cent = Centrality()
    
    json_data = get_json_string(json_path)
    graph = cent.get_graph_string(json_data)
    
    return graph, json_data
    
def get_arg_schemes_props(graph, json_data):
    cent = Centrality()
    
    i_nodes = cent.get_i_node_list(graph)
    
    schemes_list = []
    for node in i_nodes:
        node_id = node[0]
        node_text = node[1]

        schemes = identifyPremScheme(node_text)

        if len(schemes) < 1:
            continue
        else:
            ra_tup = (node_id,node_text, schemes)
            schemes_list.append(ra_tup)
            #get json string and replace text at ID then upload


    return schemes_list
    
def get_hevy_json(file_name, file_path):
    try:
        
        json_path = file_path + file_name + '_hevy.json'
        json_data = get_json_string(json_path)
        return json_data
    except:
        return ''
    


if __name__ == "__main__":
    json_path = str(sys.argv[1])
    graph, jsn = get_graph_json(json_path)
    target_schemes = get_arg_schemes_props(graph, jsn)
    
    
    
    
    print_path(json_path)