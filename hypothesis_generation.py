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
        
def identifyFullScheme(premise, conclusion):
    identifiedSchemes = []
    premise = premise.lower()
    conclusion = conclusion.lower()
    
    if (("similar" in premise or "generally" in premise) and ("be" in conclusion or "to be" in conclusion)):
        identifiedSchemes.append("Analogy")

    elif ("generally" in premise or "occur" in premise) or ("occur" in conclusion) :
        identifiedSchemes.append("CauseToEffect")

    elif("goal" in premise or "action" in premise) or ("ought" in conclusion or "perform" in conclusion) :
        identifiedSchemes.append("PracticalReasoning")

    elif(("all" in premise or "if" in premise) and ("be" in conclusion or "to be" in conclusion)) :
        identifiedSchemes.append("VerbalClassification")

    elif((("expert" in premise or "experience" in premise or "skill" in premise) and "said" in premise) and ("be" in conclusion or "to be" in conclusion)) :
        identifiedSchemes.append("ExpertOpinion")
    
    elif(("said" in premise)) :
        identifiedSchemes.append("PositionToKnow")

    elif(("occur" in premise or "happen" in premise) and ("should" in conclusion or "must" in conclusion)) :
        identifiedSchemes.append("PositiveConsequences")

    return identifiedSchemes
        
def identifyPremScheme(premise):
    identifiedSchemes = []

    premise = premise.lower()
    
    if (" similar " in premise or " generally " in premise):
        identifiedSchemes.append("Analogy")

    if (" generally " in premise or " occur " in premise):
        identifiedSchemes.append("CauseToEffect")

    if(" goal " in premise or " action " in premise):
        identifiedSchemes.append("PracticalReasoning")

    if(" all " in premise or " if " in premise) :
        identifiedSchemes.append("VerbalClassification")
    
    if(" occur " in premise or " happen " in premise):
        identifiedSchemes.append("PositiveConsequences")

    if(((" expert " in premise or " experience " in premise or " skill " in premise) and " said " in premise)) :
        identifiedSchemes.append("ExpertOpinion")
    
    if(" said " in premise) :
        identifiedSchemes.append("PositionToKnow")



    return identifiedSchemes
        
def get_arg_schemes_full_aif(json_path):
    cent = Centrality()
    
    
    graph, json_data = get_graph_json(json_path)
    

    ras = cent.get_ras(graph)
    ras_i_list = cent.get_full_ra_i_nodes(graph, ras)
    
    ra_changes = []
    for ns in ras_i_list:
        
        ra_id = ns[0]
        conc_id = ns[1]
        conc_text = ns[2]
        prem_id = ns[3]
        prem_text = ns[4]
        

        schemes = identifyFullScheme(prem_text, conc_text)

        if len(schemes) < 1:
            continue
        else:
            ra_tup = (ra_id, conc_text, prem_text,  schemes)
            ra_changes.append(ra_tup)

    

    return ra_changes
    
def get_rules(json_path):
    cent = Centrality()
    
    json_data = get_json_string(json_path)
    graph = cent.get_graph_string(json_data)
    

    ras = cent.get_ras(graph)
    ras_i_list = cent.extract_rule_structure(graph, ras)
    
    return ras_i_list
    
def get_hevy_event(node_id, hevy_json):
    
    for edge in hevy_json['edges']:
        from_id = edge['fromID']
        to_id = edge['toID']
        if str(from_id) == str(node_id):
            for node in hevy_json['nodes']:
                node_id = node['nodeID']
                
                if str(node_id) == str(to_id):
                    node_type = ''
                    try:
                        node_type = node['type']
                    except: 
                        pass
                    
                    if node_type == 'Event':
                        return node
                        
    return ''
    
def get_hevy_rules(rules, hevy_json):
    heavy_rule = []
    for rule in rules:
        hyp_id = rule[0]
        hyp_text = rule[1]
        premise_list = rule[2]
        
        
        for i, premise in enumerate(premise_list):
            premise_id = premise[0]
            premise_text = premise[1]
            if hevy_json == '':
                premise_list[i] = (premise_id, premise_text, '')
            else:
                premise_node = get_hevy_event(premise_id, hevy_json)
                premise_list[i] = (premise_id, premise_text, premise_node)
    return rules
        
        
        
        
def get_rules_data(rules_path, hevy_rules_path):
    data = []
    rules = []
    file_path = os.path.join(rules_path, '*.json')
    for file_name in glob(file_path):
    
        base=os.path.basename(file_name)

        base_ext = os.path.splitext(base)[0]
    
        schemes = get_arg_schemes_full_aif(file_name)
        rule = get_rules(file_name)
        h_jsn = get_hevy_json(base_ext, hevy_rules_path)
        rule = get_hevy_rules(rule,h_jsn)

        rules.extend(rule)
        data.extend(schemes)
    full_scheme_data = [x for x in data if x]
    return rules, full_scheme_data
    


if __name__ == "__main__":
    json_path = str(sys.argv[1])
    graph, jsn = get_graph_json(json_path)
    target_schemes = get_arg_schemes_props(graph, jsn)
    
    
    rules_path = 'rules/'
    hevy_rules_path = 'rules/hevy/'
    
    rules, full_scheme_data = get_rules_data(rules_path, hevy_rules_path)
    
    print_path(json_path)