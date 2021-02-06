import sys
import json
import statistics
from centrality import Centrality
from glob import glob
import spacy
from SentenceSimilarity import SentenceSimilarity
from itertools import combinations
import datetime
import copy
import re

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
    
def get_graph(jsn):
    cent = Centrality()
    
    graph = cent.get_graph_string(jsn)
    
    return graph
    
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
    
def get_entity_from_text(nlp, text):
    text = text.lower()
    doc = nlp(text)
    person_list=[]
    org_list = []
    place_list = []
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            person_list.append(ent.text)
        if ent.label_ == 'ORG':
            org_list.append(ent.text)
        if ent.label_ == 'GPE':
            place_list.append(ent.text)
    for token in doc:
        if token.pos_ == 'PROPN' and not any(token.text in s for s in person_list) and not any(token.text in s for s in org_list) and any(token.text in s for s in place_list):
            person_list.append(token.text)
    return person_list, org_list
    
    
def get_scheme_cq_hypothesis(scheme_type, text,node_id, agent, match, matching_proposition):
    
    scheme_hyps = []
    
    if scheme_type == "CauseToEffect":
        scheme_hyps.append("There is no other cause for effect " + text, text, node_id, scheme_type)
    if scheme_type == "PracticalReasoning":
        scheme_hyps.append((agent + " has the means to carry out the action", text ,node_id, scheme_type))
        scheme_hyps.append((agent + " does not have other conflicting goals", text ,node_id, scheme_type))
    
    if scheme_type == "VerbalClassification":
        scheme_hyps.append(("There is doubt that " + agent + " has property " + text, text ,node_id, scheme_type))
    if scheme_type == "ExpertOpinion":
        scheme_hyps.append((agent + " is a credible expert", text ,node_id, scheme_type))
        scheme_hyps.append((agent + " is an expert in the field", text ,node_id, scheme_type))
        scheme_hyps.append((agent + " is a trusted source of information", text ,node_id, scheme_type))
        scheme_hyps.append((agent + " provides consistent information", text ,node_id, scheme_type))
        scheme_hyps.append((agent + " has provided proof", text ,node_id, scheme_type))
    if scheme_type == "PositionToKnow":
        scheme_hyps.append((agent + " provides consistent information", text ,node_id, scheme_type))
        scheme_hyps.append((agent + " is in a position to know the truth", text ,node_id, scheme_type))
        scheme_hyps.append((agent + " is a trusted source of information", text ,node_id, scheme_type))
        scheme_hyps.append((agent + " has provided proof", text ,node_id, scheme_type))
        
        
    if scheme_type == "PositiveConsequences":
        scheme_hyps.append(("There is a high chance that " + text + ' will occur', text ,node_id, scheme_type))
        scheme_hyps.append(("There are not other releveant consequences of " + text, text ,node_id, scheme_type))
    return scheme_hyps
    
def get_argument_scheme_hypotheses(nlp, threshold, full_scheme_data, target_schemes):
    hyps = []
    new_hyps = []
    for scheme_tup in target_schemes:
        
        node_id = scheme_tup[0]
        node_text = scheme_tup[1]
        scheme_list = scheme_tup[2]
        agent_list = []
        org_list = []
        speaker = ''
        if 'said' in node_text.lower():
            sep = 'said'
            speaker = node_text.lower().split(sep, 1)[0]
            stripped = node_text.lower().split(sep, 1)[1]
            agent_list, org_list = get_entity_from_text(nlp, stripped)
        else:
            agent_list, org_list = get_entity_from_text(nlp, stripped)

        
        output_hyps = compare_schemes(full_scheme_data, scheme_list, hyps, speaker, node_text, node_id, threshold, agent_list)
        new_hyps.extend(output_hyps)
        
    new_hyps = list(set(new_hyps))
    return new_hyps
    
def compare_schemes(full_scheme_data, scheme_list, hyps, speaker, node_text, node_id, threshold, agent_list):
    for scheme in scheme_list:
            if len(full_scheme_data) > 0:
                for full_scheme in full_scheme_data:
                    ra_id = full_scheme[0]
                    hypothesis = full_scheme[1]
                    premise = full_scheme[2]
                    full_scheme_list = full_scheme[3]
                
                    for s in full_scheme_list:
                        if s == scheme:
                            sim = get_alternate_wn_similarity(str(node_text), str(premise))
                            if sim >= threshold:
                                if len(agent_list) < 1:
                                    hypothesis = hypothesis.replace('Person X', org_list[0])
                                    hyps.append((hypothesis, node_text, node_id, scheme))
                                else:
                                    hypothesis = hypothesis.replace('Person X', agent_list[0])
                                    hyps.append((hypothesis, node_text, node_id, scheme))
            if speaker == '':
                hyps.extend(get_scheme_cq_hypothesis(scheme, node_text,node_id, agent_list[0], False, ''))
            else:
                hyps.extend(get_scheme_cq_hypothesis(scheme, node_text,node_id, speaker, False, ''))
    return hyps
    
def get_alternate_wn_similarity(sent1, sent2):
    sent_sim = SentenceSimilarity()
    similarity = sent_sim.symmetric_sentence_similarity(sent1, sent2)
    return similarity
    

def get_prop_pairs(props, volume):
    pairs = list(combinations(props,volume))
    return pairs
    
def get_event_similarity(e1, e2):
    
    sim_list = []
    
    
    e1_name = ''
    e2_name = ''
    e1_circa = ''
    e2_circa = ''
    
    e1_inSpace = ''
    e2_inSpace = ''
    
    e1_agent = ''
    e2_agent = ''
    
    e1_involved = ''
    e2_involved = ''
    
    e1_time = ''
    e2_time = ''
    
    
    e1_place = ''
    e2_place = ''
    
    e1_ill = ''
    e2_ill = ''
    
    
    
    try:
        e1_name = e1['name']
        e2_name = e2['name']
    except:
        pass
    
    try:
        e1_circa = e1['circa']
        e2_circa = e2['circa']
    except:
        pass
    
    try:
        e1_inSpace = e1['inSpace']
        e2_inSpace = e2['inSpace']
    except:
        pass
    
    try:
        e1_agent = e1['involvedAgent']
        e2_agent = e2['involvedAgent']
    except:
        pass
    
    try:
    
        e1_involved = e1['involved']
        e2_involved = e2['involved']
    except:
        pass
    
    try:
        e1_time = e1['atTime']
        e2_time = e2['atTime']
    except:
        pass
    
    try:
        e1_place = e1['atPlace']
        e2_place = e2['atPlace']
    except:
        pass
    
    try:
        e1_ill = e1['illustrate']
        e2_ill = e2['illustrate']
    except:
        pass
    
    if e1_name == '' or e2_name == '':
        pass
    elif e1_name == e2_name:
        sim_list.append(1)
    else:
        name_sim = get_alternate_wn_similarity(e1_name, e2_name)
        sim_list.append(name_sim)
    
    if e1_circa == '' or e2_circa == '':
        pass
    elif e1_circa == e2_circa:
        sim_list.append(1)
    else:
        circa_sim = get_alternate_wn_similarity(e1_circa, e2_circa)
        sim_list.append(circa_sim)
    
    if e1_inSpace == '' or  e2_inSpace == '':
        pass
    
    elif e1_inSpace == e2_inSpace:
        sim_list.append(1)
    else:
        space_sim = get_alternate_wn_similarity(e1_inSpace, e2_inSpace)
        sim_list.append(space_sim)
        
    if isinstance(e1_agent, str) and isinstance(e2_agent, str):
        if e1_agent == '' or e2_agent == '':
            pass
        elif e1_agent == e2_agent:
            sim_list.append(1)
        else:
            agent_sim = get_alternate_wn_similarity(e1_agent, e2_agent)
            sim_list.append(agent_sim)
    else:
        e1_agent = ' '.join(e1_agent)
        if e1_agent == '' or e2_agent == '':
            pass
        elif e1_agent == e2_agent:
            sim_list.append(1)
        else:
            agent_sim = get_alternate_wn_similarity(e1_agent, e2_agent)
            sim_list.append(agent_sim)
        
    if e1_involved == '' or e2_involved == '':
        pass
    elif e1_involved == e2_involved:
        sim_list.append(1)
    else:
        inv_sim = get_alternate_wn_similarity(e1_involved, e2_involved)
        sim_list.append(inv_sim)
        
    if e1_time == '' or e2_time == '':
        pass
    elif e1_time == e2_time:
        sim_list.append(1)
    else:
        time_sim = get_alternate_wn_similarity(e1_time, e2_time)
        sim_list.append(time_sim)
        
    if e1_place == '' or e2_place == '':
        pass
    elif e1_place == e2_place:
        sim_list.append(1)
    else:
        place_sim = get_alternate_wn_similarity(e1_place, e2_place)
        sim_list.append(place_sim)
        
    if e1_ill == '' or  e2_ill == '':
        pass
    elif e1_ill == e2_ill:
        sim_list.append(1)
    else:
        ill_sim = get_alternate_wn_similarity(e1_ill, e2_ill)
        sim_list.append(ill_sim)
  

    
    harm_mean = statistics.mean(sim_list)
    
    return harm_mean
    
    
def create_rule_hypothesis(score_store, rule_id, rule_hyp, prem_id, nlp):
    
    overall_hypothesis_list = []
    
    for score in score_store:
                
        matched_premise = score[0]
        matched_rule_premise = score[1]
        sim = score[2]
        rule_type = score[3]
        agent = ''
        agent_list = []
        org_list = []
        overall_hyp = ''
                
                
                
        if rule_type == 'EVENT RULE':
            ev_premise = score[4]
            agent = ev_premise['involvedAgent']
            if not isinstance(agent, str):
                agent = agent[0]
        else:
                    
            agent_list, org_list = get_entity_from_text(nlp, matched_premise)
        if 'Person X' in rule_hyp and len(agent_list) > 0:
            agent = agent_list[0]
            overall_hyp = rule_hyp.replace('Person X', agent)
            #overall_hypothesis_list.append(overall_hyp)
        elif 'Person X' in rule_hyp:
            overall_hyp = rule_hyp.replace('Person X', agent)
            #overall_hypothesis_list.append(overall_hyp)
                
        overall_hypothesis_list.append([overall_hyp,rule_id, matched_premise, matched_rule_premise, sim, rule_type, prem_id, 'Default Inference'])
    return overall_hypothesis_list
    
    
def compare_rules_to_props(target_nodes, rule_premises, rule_id, rule_hyp, nlp, hevy_jsn, threshold):
    overall_hyp_list = []
    for target in target_nodes:
    
        rule_flag = True
        score_store = []
        for prem in target:
            l = [None] * len(target)
            counter = 0
            for r in rule_premises:
                rule_text = r[1]
                rule_event = r[2]
                prem_id = prem[0]
                prem_text = prem[1]
                prem_event = ''
                try:
                    prem_event = get_hevy_event(prem_id, hevy_jsn)
                except:
                    pass
                sim = 0
                event_flag = False
                if prem_event == '' or rule_event == '':
                    sim = get_alternate_wn_similarity(prem[1], rule_text)
                else:
                    sim = get_event_similarity(prem_event, rule_event)
                    event_flag = True
                
                if event_flag:
                    if sim >= (threshold): #threshold * 2
                        
                        score_store.append((prem_text, rule_text, sim, 'EVENT RULE', prem_event))
                    
                        l[counter] = 1
                    else:
                        l[counter] = 0
                    counter = counter + 1
                else:
                    if sim >= (threshold * 2):
           
                        score_store.append((prem_text, rule_text, sim, 'SIM RULE', ''))
                       
                        l[counter] = 1
                    else:
                        l[counter] = 0
                    counter = counter + 1
            if sum(l) < 1:
                rule_flag = False
                break
    
        if rule_flag:

            hyps = create_rule_hypothesis(score_store, rule_id, rule_hyp, prem_id, nlp)
            overall_hyp_list.extend(hyps)
            
    return overall_hyp_list
    
def get_hyps_from_rules(hevy_jsn, i_nodes, rules, threshold, nlp):
    all_hypothesis_list = []
    for rule in rules:
        rule_id = rule[0]
        rule_hyp = rule[1]
        rule_premises = rule[2]
        premise_volume = len(rule_premises)
    
    
        target_nodes = get_prop_pairs(i_nodes, premise_volume)
        
        hypothesis_list = compare_rules_to_props(target_nodes, rule_premises, rule_id, rule_hyp, nlp, hevy_jsn, threshold)
        all_hypothesis_list.extend(hypothesis_list)
    return all_hypothesis_list
    
def remove_duplicate_hypos(overall_hypothesis_list):
    d = {}
    for sub in overall_hypothesis_list:
        hyp_name = sub[0]
        hyp_id = sub[1]
        prem = sub[2]
        sim = sub[4]
        hyp_name = hyp_name.lower()
        key_string = str(hyp_name) + str(hyp_id) + str(prem)
    
        if key_string in d:
            if sim > d[key_string][4]:
                d[key_string] = sub
        else:
        
            d[key_string] = sub
    return list(d.values())
    
def combine_hypothesis_lists(arg_schemes_hyps, rules_hyps):
    new_arg_scheme_list = []
    for hyp in arg_schemes_hyps:
        hypothesis = hyp[0].lower()
        premise = hyp[1].lower()
        premise_id = hyp[2]
        scheme_type = hyp[3]
        rule_flag = False
        for i,hyp1 in enumerate(rules_hyps):
            hypothesis1 = hyp1[0].lower()
            rules_hyps[i][0] = hypothesis1
            premise1 = hyp1[2].lower()
            scheme_type1 = hyp1[7]
            if hypothesis == hypothesis1 and premise == premise1:
                rule_flag = True
                rules_hyps[i][7] = scheme_type
        
        if not rule_flag:
            new_arg_scheme_list.append([hypothesis, '', premise, '', 0, 'SCHEME RULE', premise_id, scheme_type])
    
    return new_arg_scheme_list, rules_hyps
    
def get_node_ID(graph_jsn, text):
    for node in graph_jsn['nodes']:
        n_text = node['text']
        n_id = node['nodeID']
        if text == n_text:
            return n_id
        
    return ''
    
def create_hyp_ya(node_id):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ya_dict = {"nodeID":node_id,"text":"Hypothesising","type":"YA","timestamp":timestamp,"scheme":"Hypothesising","schemeID":"410"}
    return ya_dict
    
def create_l_node(node_id, text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    l_text = 'Hypothesis Generator : ' + text
    l_dict = {"nodeID":node_id,"text":l_text,"type":"L","timestamp":timestamp}
    return l_dict
    
def create_ra_node(node_id, text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    ra_dict = {"nodeID":node_id,"text":text,"type":"RA","timestamp":timestamp}
    return ra_dict
    
def create_edge(edge_id, fromID, toID):
    edge_dict = {"edgeID":edge_id,"fromID":fromID,"toID":toID}
    return edge_dict
    
def check_hyp_list(hyp, rule_list):
    
    
    hypothesis = hyp[0]
    rule_number = hyp[1]
    premise = hyp[2]
    rule_premise = hyp[3]
    sim = hyp[4]
    rule_type = hyp[5]
    ra_type = hyp[7]
    
    hyp_check = True
    rule_check = True
    prem_check = True
    
    for rule in rule_list:
        
        
        
        r_hypothesis = rule[0]
        r_rule_number = rule[1]
        r_premise = rule[2]
        r_rule_premise = rule[3]
        r_sim = rule[4]
        r_rule_type = rule[5]
        r_ra_type = rule[7]
        r_ra_id = rule[8]
        
            
        
        if hypothesis == r_hypothesis and rule_number == r_rule_number and premise == r_premise:
            #Already a connected made so return all false
            return False,'False'
        
        if hypothesis == r_hypothesis and rule_number == r_rule_number and premise != r_premise:
            return True, r_ra_id
        
        if hypothesis != r_hypothesis:
            hyp_check = False
        
        if hypothesis == r_hypothesis and rule_number != r_rule_number:
            rule_check = False
            
    if not hyp_check:
        return False, ''
    
    if not rule_check:
        return False, ''
    
    return False,'False'
    
def change_ra_type(ra_id, node_list, ra_type):
    for node in node_list:
        if node['nodeID'] == ra_id:
            curr_ra_text = node['text']
            if curr_ra_text == 'Default Inference' and ra_type != 'Default Inference':
                node['text'] = ra_type
                

def construct_aif_graph(hypotheses, jsn):
    new_node_list = []
    new_edge_list = []
    rule_lst = []
    
    for i, hyp in enumerate(hypotheses):
        hypothesis = hyp[0]
        rule_number = hyp[1]
        premise = hyp[2]
        rule_premise = hyp[3]
        sim = hyp[4]
        rule_type = hyp[5]
        p_id = hyp[6]
        ra_type = hyp[7]
        
        #n_id = get_node_ID(jsn, hypothesis)
        #n_id == '' and 
        if not any(d['text'] == hypothesis for d in new_node_list):
            #create node
            n_id = "H" + str(i)
            node_id = "H" + str(i)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            node_dict = {"nodeID": node_id, "text": hypothesis, "type":"I", "timestamp":timestamp}
            ya_id = "YA" + str(i)
            ya_node = create_hyp_ya(ya_id)
            l_id = "L" + str(i)
            L_node = create_l_node(l_id, hypothesis)
            edge1_id = 'E1H' + str(i)
            edge_1 = create_edge(edge1_id, l_id, ya_id)
            
            edge2_id = 'E2H' + str(i)
            edge_2 = create_edge(edge2_id, ya_id, node_id)
            
            new_node_list.append(node_dict)
            new_node_list.append(ya_node)
            new_node_list.append(L_node)
            
            new_edge_list.append(edge_1)
            new_edge_list.append(edge_2)
            
        check_bool = False
        id_str = ''
            
        #Here create RAS and edges from premises to the RAs
        premise_id = get_node_ID(jsn, premise)
        if len(rule_lst) > 0:
            check_bool, id_str = check_hyp_list(hyp, rule_lst)
        
        if rule_number == '':
            ra_id = 'RA' + str(i)
            new_ra_node = create_ra_node(ra_id, ra_type)
            
            edge1_id = 'EH' + str(i)
            edge_1 = create_edge(edge1_id, p_id, ra_id)
            
            edge2_id = 'EHT' + str(i)
            edge_2 = create_edge(edge2_id, ra_id, n_id)

            
            new_node_list.append(new_ra_node)
            new_edge_list.append(edge_1)
            new_edge_list.append(edge_2)
            
        elif len(rule_lst) < 1: 
            ra_id = 'RA' + str(i)
            new_ra_node = create_ra_node(ra_id, ra_type)
            
            edge1_id = 'EH' + str(i)
            edge_1 = create_edge(edge1_id, premise_id, ra_id)
            
            edge2_id = 'EHT' + str(i)
            edge_2 = create_edge(edge2_id, ra_id, n_id)
            
            
            hyp.append(ra_id)
            rule_lst.append(hyp)
            
            new_node_list.append(new_ra_node)
            new_edge_list.append(edge_1)
            new_edge_list.append(edge_2)
            
        elif not check_bool and id_str == 'False':
            pass
        elif check_bool:
            
            #GET RA TO CHECK TYPE
            change_ra_type(id_str,new_node_list, ra_type)
            
            edge1_id = 'EH' + str(i)
            edge_1 = create_edge(edge1_id, premise_id, id_str)
            
            
            hyp.append(id_str)
            rule_lst.append(hyp)
            new_edge_list.append(edge_1)
        elif not check_bool and id_str == '':
            ra_id = 'RA' + str(i)
            new_ra_node = create_ra_node(ra_id, ra_type)
            
            edge1_id = 'EH' + str(i)
            edge_1 = create_edge(edge1_id, premise_id, ra_id)
            
            edge2_id = 'EHT' + str(i)
            edge_2 = create_edge(edge2_id, ra_id, n_id)
            
            hyp.append(ra_id)
            rule_lst.append(hyp)
            
            new_node_list.append(new_ra_node)
            new_edge_list.append(edge_1)
            new_edge_list.append(edge_2)
    
    return new_node_list, new_edge_list
    
def get_hypotheses_list(jsn_data):
    nodes = jsn_data['nodes']
    edges = jsn_data['edges']
    
    hypothesis_list = []
    
    for node in nodes:
        node_id = node['nodeID']
        if node['text'] == 'Hypothesising':
            for edge in edges:
                if str(edge['fromID']) == str(node_id):
                    hyp_id = edge['toID']
                    for n in nodes:
                        n_id = n['nodeID']
                        n_text = n['text']
                        if str(n_id) == hyp_id:
                            hypothesis_list.append([hyp_id, n_text])
    return hypothesis_list
    
def generate_alternative_hypothesis(hypotheses, nlp):
    negative_hyps = []
    for hyp in hypotheses:
        h_id = hyp[0]
        h_text = hyp[1]
        doc = nlp(h_text)
        negation = [tok for tok in doc if tok.dep_ == 'neg']
        neg_flag = check_for_negation(negation)
        if neg_flag:
            pos_form = convert_to_positive_form(negation, h_text)
            negative_hyps.append([pos_form, h_id, h_text])
            
        else:
            neg_form = convert_to_negative_form(h_text, doc)
            negative_hyps.append([neg_form, h_id, h_text])
    return negative_hyps
    
def check_for_negation(negation_list):
    if len(negation_list) < 1:
        return False
    else:
        return True
        
def convert_to_positive_form(negation_list, sentence):
    negation_list = [str(x).lower() for x in negation_list]
    resultwords  = [word for word in re.split("\W+",sentence) if word.lower() not in negation_list]
    result = ' '.join(resultwords)
    return result
    
def convert_to_negative_form(sent, doc):
    for token in doc:
        if token.dep_ == 'ROOT' or token.dep_ == 'aux':
            if 'VB' in token.tag_:
                if token.tag_ == 'VBZ':
                #insert Not after
                    negation = 'not'
                    word_list = [token.text]
                    word_list = [str(x).lower() for x in word_list]
                    sent_words = re.split("\W+",sent)
                    resultwords  = [word.lower() + ' ' + negation + ' ' if word.lower() in word_list else word.lower() for word in sent_words ]
                    result = ' '.join(resultwords)
                    return result
                else:
                    negation = 'did not'
                    word_list = [token.text]
                    word_list = [str(x).lower() for x in word_list]
                    sent_words = re.split("\W+",sent)
                    resultwords  = [' ' + negation + ' ' + str(token.lemma_) if word.lower() in word_list else word.lower() for word in sent_words ]
                    result = ' '.join(resultwords)
                    return result
    return 'not ' + sent.lower()
    
def create_ca_node(node_id, text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    ca_dict = {"nodeID":node_id,"text":text,"type":"CA","timestamp":timestamp}
    return ca_dict
    
def alternate_hyps_aif(alt_hyps):
    new_node_list = []
    new_edge_list = []
    
    for i, hyp in enumerate(alt_hyps):
        alt_text = hyp[0]
        hyp_id = hyp[1]
        
        n_id = "AH" + str(i)
        node_id = "AH" + str(i)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        node_dict = {"nodeID": node_id, "text": alt_text, "type":"I", "timestamp":timestamp}
        ya_id = "AYA" + str(i)
        ya_node = create_hyp_ya(ya_id)
        
        l_id = hyp_id.replace('H', 'L')
            
        edge1_id = 'EA' + str(i)
        edge_1 = create_edge(edge1_id, l_id, ya_id)
            
        edge2_id = 'EA' + str(i)
        edge_2 = create_edge(edge2_id, ya_id, node_id)
        
        ca_1_id = 'CA' + str(i)
        ca_2_id = 'ACA' + str(i)
        
        ca_text = 'Default Conflict'
        
        ca_1_node = create_ca_node(ca_1_id, ca_text)
        ca_2_node = create_ca_node(ca_2_id, ca_text)
        
        CAedge1_id = 'CAE' + str(i)
        CAedge_1 = create_edge(CAedge1_id, hyp_id, ca_1_id)
            
        CAedge2_id = 'CAAE' + str(i)
        CAedge_2 = create_edge(CAedge2_id, ca_1_id, node_id)
        
        
        Cedge1_id = 'CE' + str(i)
        Cedge_1 = create_edge(Cedge1_id, node_id, ca_2_id)
            
        Cedge2_id = 'CEE' + str(i)
        Cedge_2 = create_edge(CAedge2_id, ca_2_id, hyp_id)
            
        new_node_list.append(node_dict)
        new_node_list.append(ya_node)
        new_node_list.append(ca_1_node)
        new_node_list.append(ca_2_node)
            
        new_edge_list.append(edge_1)
        new_edge_list.append(edge_2)
        new_edge_list.append(CAedge_1)
        new_edge_list.append(CAedge_2)
        
        new_edge_list.append(Cedge_1)
        new_edge_list.append(Cedge_2)
        
    return new_node_list, new_edge_list
    
def print_hypoths(hyps, alt_hyps):
    print('Generated the following hypotheses: ')
    print(' ')
    for hyp in hyps:
        
        
        print(hyp[1])
    print(' ')
    print('Generated the alternative hypotheses: ')
    print(' ')
    for alt_hyp in alt_hyps:
        
        
        print(alt_hyp[0])
        
def write_json_to_file(jsn, path):
    
    with open(path, 'w') as fp:
        json.dump(jsn, fp)

if __name__ == "__main__":
    json_path = str(sys.argv[1])
    graph, jsn = get_graph_json(json_path)
    target_schemes = get_arg_schemes_props(graph, jsn)
    
    
    rules_path = 'rules/'
    hevy_rules_path = 'rules/hevy/'
    
    rules, full_scheme_data = get_rules_data(rules_path, hevy_rules_path)
    nlp = spacy.load("en_core_web_sm")

    scheme_hypos = get_argument_scheme_hypotheses(nlp, 0.33, full_scheme_data, target_schemes)
    
    cent = Centrality()
    i_nodes = cent.get_i_node_list(graph)
    hevy_jsn = get_hevy_json('20088_targe', '')
    rule_hypos = get_hyps_from_rules(hevy_jsn, i_nodes, rules, 0.17, nlp)
    rule_hypo_list = remove_duplicate_hypos(rule_hypos)
    
    scheme_list, overall_rule_list = combine_hypothesis_lists(scheme_hypos, rule_hypo_list)
    
    all_hypotheses = scheme_list + overall_rule_list
    
    all_hypotheses_copy = copy.deepcopy(all_hypotheses)
    
    nodelst, edgelst = construct_aif_graph(all_hypotheses_copy, jsn)
    
    jsn_copy = copy.deepcopy(jsn)
    
    nodes_cp = jsn_copy['nodes']
    nodes_cp.extend(nodelst)
    jsn_copy['nodes'] = nodes_cp
    
    edges_cp = jsn_copy['edges']
    edges_cp.extend(edgelst)
    jsn_copy['edges'] = edges_cp

    
    hypoths_list = get_hypotheses_list(jsn_copy)
    
    alternative_hypotheses = generate_alternative_hypothesis(hypoths_list, nlp)
    
    alt_nodes, alt_edges = alternate_hyps_aif(alternative_hypotheses)
    
    alt_jsn_copy = copy.deepcopy(jsn_copy)
    
    nodes_cp = alt_jsn_copy['nodes']
    nodes_cp.extend(alt_nodes)
    alt_jsn_copy['nodes'] = nodes_cp
    
    edges_cp = alt_jsn_copy['edges']
    edges_cp.extend(alt_edges)
    alt_jsn_copy['edges'] = edges_cp
    
    
    
    
    print_hypoths(hypoths_list, alternative_hypotheses)
    write_json_to_file(alt_jsn_copy, 'generated_hyps.json')
