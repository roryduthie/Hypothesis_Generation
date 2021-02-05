import sys
import json
import statistics
from centrality import Centrality
from glob import glob
import spacy
from SentenceSimilarity import SentenceSimilarity
from itertools import combinations

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
                                    hyps.append((hypothesis, node_text, node_id))
                                else:
                                    hypothesis = hypothesis.replace('Person X', agent_list[0])
                                    hyps.append((hypothesis, node_text, node_id))
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
                
        overall_hypothesis_list.append([overall_hyp,rule_id, matched_premise, matched_rule_premise, sim, rule_type, prem_id])
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
    
    print(rule_hypos)
