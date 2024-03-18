from atomic_concepts import Atom
from name_space.name_space import NameSpace
from atomic_concepts.relation import Relation
from atomic_concepts.before import Before
from atomic_concepts.after import After
from atomic_concepts.function import Function
from atomic_concepts.var import Var
from util.legal_ml_parser import get_gdpr, get_legal_ml_root
from data_structure.rule_graph.rule_graph import rule_to_temporal_tree
from pipeline import rule_to_tree_pipeline, temporal_rule_to_tree_pipeline
from util.tree_from_rule.tree_from_rule import RuleTreesUtil
from util.transform_temporal_structure.transform import transform_temporal_rule_structure
from util.tree_modification.clean_tree import clean_tree

import numpy as np
import matplotlib.pyplot as plt
import os
import json

BOOTSTRAP_BOILERPLATE = """
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/popper.js@1.12.9/dist/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
"""

def all_temporal_rule_trees(gdpr_dict: dict, already_seen_trees: list, rule_type: str):
    if "statements" in gdpr_dict:
        for statement in gdpr_dict["statements"]:
            if not statement[2] == rule_type:
                continue
            temporal_tree = rule_to_temporal_tree(statement[0])
            res_list = [x for x in already_seen_trees if x[0].compare_tree_structure(temporal_tree)]
            if len(res_list) == 0:
                already_seen_trees.append([temporal_tree, 1])
            elif len(res_list) == 1:
                res_list[0][1] += 1
            else:
                raise Exception("More than one tree found")
    
    for key, val in gdpr_dict.items():
        if isinstance(val, list):
            continue
        all_temporal_rule_trees(val, already_seen_trees, rule_type)
    
    return already_seen_trees

def rec_html_gdpr(gdpr_dict: dict, curr_path: str):
    gdpr_text = json.load(open("html_parsing/parsed_gdpr_en.json"))
    path_pos_meaning = ["Article", "Paragraph", "List", "Point"]
    dict_path = curr_path.split("/")[1:-1]
    curr_text = gdpr_text
    bold_text = ""
    print(curr_path)
    try:
        for i in range(len(dict_path)):
            path = dict_path[i]
            curr_text = curr_text[path]
            if "title" in curr_text and isinstance(curr_text["title"], str):
                bold_text += f'<h5>{path_pos_meaning[i]}:</h5><p>{curr_text["title"]}</p> </br>'
            if "title" in curr_text and "title" in curr_text["title"]:
                bold_text += f'<h5>{path_pos_meaning[i]}:</h5>{curr_text["title"]["title"]} </br>'
            
            if "text" in curr_text and "title" in curr_text["text"]:
                bold_text += f'<h5>{path_pos_meaning[i]}:</h5>{curr_text["text"]["title"]}</br>'
                
            if "text" in curr_text:
                bold_text += f'<h5>{path_pos_meaning[i]}:</h5>{curr_text["text"]}</br>'
            if isinstance(curr_text, str):
                bold_text += f'<h5>{path_pos_meaning[i]}:</h5>{curr_text}</br>'

    except:
        curr_text = ""
    bold_text = f'<div class="card"> <div class="card-body"> {bold_text} </div></div>'
    statement_code = ""
    if len(bold_text) > 0:
        statement_code += f"<div>{bold_text}</div></br>"
    if "statements" in gdpr_dict:
        statement_code += "<div>"
        statement_num = 0
        for i in range(len(gdpr_dict["statements"])):
            statement = gdpr_dict["statements"][i]
            statement_code += f"<b>Statement {statement_num}</b></br>"
            statement_code += '<div class="card"> <div class="card-body">'
            statement_code += f"<b class='text-start'>Raw Dapreco, Compact</b><div class='col-8 d-flex flex-column justify-content-center align-items-center'><code>{str(statement[0])}</code></div></br>"
            #tree_string = rule_to_tree_pipeline(statement[0]).printNTree().replace('\n', '<br>')
            #statement_code += f"<div class='col-8 d-flex flex-column justify-content-center align-items-center'><pre><code>{tree_string}</code></pre></div></br>"
            temporal_tree_string = rule_to_temporal_tree(statement[0]).printNTree().replace('\n', '<br>')
            statement_code += f"<b class='text-start'>Temporal Relations</b><div class='col-8 d-flex flex-column justify-content-center align-items-center'><pre><code>{temporal_tree_string}</code></pre></div></br>"
            #temporal_tree = transform_temporal_rule_structure(statement[0])
            #temporal_tree_inserted_temporal_id = temporal_tree.printNTree().replace('\n', '<br>')
            #statement_code += f"<div class='col-8 d-flex flex-column justify-content-center align-items-center'><pre><code>{temporal_tree_inserted_temporal_id}</code></pre></div></br>"
            temporal_flat_tree = temporal_rule_to_tree_pipeline(statement[0])
            #statement_code += f"<div class='col-8 d-flex flex-column justify-content-center align-items-center'><pre><code>{temporal_flat_tree.printNTree()}</code></pre></div></br>"
            manual_mfotl_path = f"whyenf_files_manual{curr_path}formula{(i+1)}_u.mfotl"
            temporal_tree_mfotl_flat_str = ""
            if os.path.isfile(manual_mfotl_path):
                temporal_tree_mfotl_flat_str = open(manual_mfotl_path).read()
            else:
                temporal_tree_mfotl_flat_str = temporal_flat_tree.get_printable_tree_with_duplicates()
            statement_code += f"<b class='text-start'>MFOTL Output</b><div class='col-8 d-flex flex-column justify-content-center align-items-center'><code>{temporal_tree_mfotl_flat_str}</code></div></br>"
            statement_code += '</div></div>'
            statement_code += "<hr class='hr' />"
            statement_num += 1
        statement_code += "</div>"
    
    
  
    link_code = '<div class="btn-group-vertical" role="group" aria-label="Vertical button group">'
    for key, val in gdpr_dict.items():
        if isinstance(val, list):
            continue
        
        this_path = curr_path + key + "/"
        rec_html_gdpr(val, this_path)
        f'<button type="button" class="btn btn-primary">Button</button>'
        link_code += f"<a class='btn btn-outline-primary' href='./{key}/rule.html' role='button' >{this_path} </a>"
    link_code += "</div>"
    
    html_code = f"""<head>{BOOTSTRAP_BOILERPLATE}</head><body  class="p-3 m-0 border-0 bd-example m-0 border-0">
    <div><h2>{curr_path}</h2></div>
    {link_code}
    <br>
    <a class="btn btn-secondary" href="../rule.html" role="button">GO BACK</a>
    <br>{statement_code}</body>"""
    
    relative_path = f"html_parsing/html{curr_path}"
    # TODO: This might cause problems with absolute paths
    if not os.path.exists(relative_path):
        os.makedirs(relative_path)
        
    html_file = open(f"html_parsing/html{curr_path}rule.html", "w+")
    html_file.write(html_code)
    html_file.close()

def make_gdpr_rules_to_html():
    root = get_legal_ml_root("rioKB_GDPR.xml")
    gdpr = get_gdpr(root).get_articles()
    rec_html_gdpr(gdpr, "/")
    
def make_gdpr_temporal_rules_to_html():
    root = get_legal_ml_root("rioKB_GDPR.xml")
    gdpr = get_gdpr(root).get_articles()
    rule_types = [NameSpace.RIOONTO.value + ":obligationRule", NameSpace.RIOONTO.value + ":constitutiveRule", NameSpace.RIOONTO.value + ":permissionRule"]
    statement_code = ""
    statement_code += "<div class='container-fluid'>"
    statement_code += "<div class='row'>"
    for rule_type in rule_types:
        statement_code += f"<div class='col-4'> {rule_type}<hr class='hr' />"
        temporal_trees = all_temporal_rule_trees(gdpr, [], rule_type)
        temporal_trees.sort(key=lambda x: x[1], reverse=True)
        
        for temporal_tree in temporal_trees:
            temporal_tree_string = temporal_tree[0].printNTree().replace('\n', '<br>')
            num_temporal_trees_seen = temporal_tree[1]
            statement_code += f"""<div>
            Num occurences: {num_temporal_trees_seen}</br>
            <pre style='margin:0. display:inline'>{temporal_tree_string}</pre></div></br>
            <hr class='hr' />"""
        
        statement_code += "</div>"
    statement_code += "</div></div>"
    html_code = f"""<head>{BOOTSTRAP_BOILERPLATE}</head><body>{statement_code}</body>"""
    
    html_file = open(f"html_parsing/unique_trees/unique_trees.html", "w+")
    html_file.write(html_code)
    html_file.close()
    
    print(len(temporal_trees))

def make_predicate_signatures_to_html():
    root = get_legal_ml_root("rioKB_GDPR.xml")
    gdpr = get_gdpr(root).get_articles()
    
    rule_tree_utils = []
    article_queue = [gdpr]
    while len(article_queue) > 0:
        curr_paragraph = article_queue.pop(0)
        for key, article_content in curr_paragraph.items():
            if key == "statements":
                for statement in article_content:
                    rule_tree_utils.append(RuleTreesUtil(statement[0]))
            else:
                article_queue.append(article_content)
    
    signatures = {}
    while len(rule_tree_utils) > 0:
        curr_tree_util = rule_tree_utils.pop(0)
        trees = curr_tree_util.if_trees.copy()
        for then_tree in curr_tree_util.then_trees:
            trees.append(then_tree)
        [clean_tree(x) for x in trees]
        
        """for tree in trees:
            queue = [tree]
            while len(queue) > 0:
                curr = queue.pop()
                for i in range(len(curr.relations)):
                    child = curr.relations[i]
                    if child.parent_relation != curr.parent_relation:
                        continue
                    for j in range(len(child.relations)):
                        childs_child = child.relations[j]
                        if child.var == childs_child.var:
                            curr.relations[i] = childs_child
        
                    queue.append(child)
        """
        while len(trees) > 0:
            curr_tree = trees.pop(0)
            
            if not isinstance(curr_tree.parent_relation, Atom):
                continue
            
            relation_name = curr_tree.parent_relation.get_atom_content()[0].get_rel_name()
            if relation_name not in signatures:
                signatures[relation_name] = {}
            
            child_relations = []
            for i in range(len(curr_tree.relations)):
                child = curr_tree.relations[i]
                if child.parent_relation == curr_tree.parent_relation and len(child.relations) == 1:
                    trees.append(child.relations[0])
                    child_relations.append(child.relations[0].parent_relation.get_atom_content()[0].get_rel_name())
                else:
                    trees.append(child)
                    child_relations.append(child.parent_relation.get_atom_content()[0].get_rel_name())
            
            child_relations = tuple(child_relations)
            
            if child_relations in signatures[relation_name]:
                signatures[relation_name][child_relations] += 1
            else:
                signatures[relation_name][child_relations] = 1
            
    for key, val in signatures.items():
        print(f"key: {key}: num_sigs: {len(val)}")

    statement_code = "<div class='container-fluid'>"
    statement_code += "<div class='row'>"
    
    for key, val in signatures.items():
        statement_code += "<div class='col-4'>"
        
        statement_code += "<b>" + key + "</b>"
        
        sig_items = []
        for sig, occurs in val.items():
            sig_items.append([sig, occurs])
        sig_items.sort(key=lambda x: x[1], reverse=True)
        for sig, occurences in sig_items:
            statement_code += f"<div> {sig} - {occurences} </div>"
        statement_code += "</div><hr class='hr' />"
    
    
    html_code = f"""<head>{BOOTSTRAP_BOILERPLATE}</head><body>{statement_code}</body>"""
    
    html_file = open(f"html_parsing/signatures/signatures.html", "w+")
    html_file.write(html_code)
    html_file.close()

def make_predicate_signatures_with_arg_name_to_html():
    root = get_legal_ml_root("rioKB_GDPR.xml")
    gdpr = get_gdpr(root).get_articles()
    
    rule_tree_utils = []
    article_queue = [gdpr]
    while len(article_queue) > 0:
        curr_paragraph = article_queue.pop(0)
        for key, article_content in curr_paragraph.items():
            if key == "statements":
                for statement in article_content:
                    rule_tree_utils.append(RuleTreesUtil(statement[0]))
            else:
                article_queue.append(article_content)
    
    signatures = {}
    while len(rule_tree_utils) > 0:
        curr_tree_util = rule_tree_utils.pop(0)
        trees = curr_tree_util.if_trees.copy()
        for then_tree in curr_tree_util.then_trees:
            trees.append(then_tree)
        [clean_tree(x) for x in trees]
        
        """for tree in trees:
            queue = [tree]
            while len(queue) > 0:
                curr = queue.pop()
                for i in range(len(curr.relations)):
                    child = curr.relations[i]
                    if str(child.parent_relation) != str(curr.parent_relation) or len(child.relations) == 0:
                        queue.append(child)
                        continue
                    if len(child.relations) == 1:
                        childs_child = child.relations[0]
                        curr.relations[i] = childs_child
                        queue.append(childs_child)
                    else:
                        queue.append(child)
        """                        
        seen_predicates = {}
        
        print(trees[0].printNTree())
        while len(trees) > 0:
            curr_tree = trees.pop(0)
            
            if not isinstance(curr_tree.parent_relation, Atom):
                continue
            
            relation_name = curr_tree.parent_relation.get_atom_content()[0].get_rel_name()
            predicate = str(curr_tree.parent_relation)
            if relation_name not in signatures:
                signatures[relation_name] = {}
            if predicate not in seen_predicates:
                seen_predicates[predicate] = len(curr_tree.parent_relation.get_atom_content()[0].get_rel_content())-1
                
            child_relations = []
            for i in range(len(curr_tree.relations)):
                child = curr_tree.relations[i]
                if str(child.parent_relation) == str(curr_tree.parent_relation):
                    for grandchild in child.relations:
                        
                        to_add = f"{grandchild.parent_relation.get_atom_content()[0].get_rel_name()} - {grandchild.var}"
                        if to_add not in child_relations:
                            child_relations.append(to_add)
                
                else:
                    trees.append(child)
                    to_add = f"{child.parent_relation.get_atom_content()[0].get_rel_name()} - {child.var}"
                    if to_add not in child_relations:
                        child_relations.append(to_add)
            
            child_relations = tuple(child_relations)
            if len(child_relations) < seen_predicates[predicate]:
                continue
            if child_relations in signatures[relation_name]:
                signatures[relation_name][child_relations] += 1
            else:
                signatures[relation_name][child_relations] = 1
            

    statement_code = "<div class='container-fluid'>"
    statement_code += "<div class='row'>"
    
    for key, val in signatures.items():
        statement_code += "<div class='col-4'>"
        
        statement_code += "<b>" + key + "</b>"
        
        tot_occurs = 0
        sig_items = []
        for sig, occurs in val.items():
            sig_items.append([sig, occurs])
            tot_occurs += occurs
        sig_items.sort(key=lambda x: x[1], reverse=True)
        for sig, occurences in sig_items:
            statement_code += f"<div> {sig} - {occurences/tot_occurs} </div>"
        statement_code += "</div><hr class='hr' />"
    
    
    html_code = f"""<head>{BOOTSTRAP_BOILERPLATE}</head><body>{statement_code}</body>"""
    
    html_file = open(f"html_parsing/signatures/signatures_with_arg_name.html", "w+")
    html_file.write(html_code)
    html_file.close()

def ids_per_predicate_to_html():
    root = get_legal_ml_root("rioKB_GDPR.xml")
    gdpr = get_gdpr(root).get_articles()
    
    rule_tree_utils = []
    article_queue = [gdpr]
    while len(article_queue) > 0:
        curr_paragraph = article_queue.pop(0)
        for key, article_content in curr_paragraph.items():
            if key == "statements":
                for statement in article_content:
                    rule_tree_utils.append(RuleTreesUtil(statement[0]))
            else:
                article_queue.append(article_content)
    
    signatures = {}
    while len(rule_tree_utils) > 0:
        curr_tree_util = rule_tree_utils.pop(0)
        trees = curr_tree_util.if_trees.copy()
        for then_tree in curr_tree_util.then_trees:
            trees.append(then_tree)
        [clean_tree(x) for x in trees]
        
        """for tree in trees:
            queue = [tree]
            while len(queue) > 0:
                curr = queue.pop()
                for i in range(len(curr.relations)):
                    child = curr.relations[i]
                    if child.parent_relation != curr.parent_relation:
                        continue
                    for j in range(len(child.relations)):
                        childs_child = child.relations[j]
                        if child.var == childs_child.var:
                            curr.relations[i] = childs_child
        
                    queue.append(child)
        """
        while len(trees) > 0:
            curr_tree = trees.pop(0)
            
            if not isinstance(curr_tree.parent_relation, Atom):
                continue
            
            relation_name = curr_tree.parent_relation.get_atom_content()[0].get_rel_name()
            if relation_name not in signatures:
                signatures[relation_name] = {}
            
            for i in range(len(curr_tree.relations)):
                child = curr_tree.relations[i]
                if child.parent_relation == curr_tree.parent_relation and len(child.relations) == 1:
                    trees.append(child.relations[0])
                else:
                    trees.append(child)
            
            rel_identifior = curr_tree.parent_relation.get_atom_content()[0].get_rel_content()[0]
            
            if rel_identifior in signatures[relation_name]:
                signatures[relation_name][rel_identifior] += 1
            else:
                signatures[relation_name][rel_identifior] = 1
            
    for key, val in signatures.items():
        print(f"key: {key}: num_sigs: {len(val)}")

    statement_code = "<div class='container-fluid'>"
    statement_code += "<div class='row'>"
    
    for key, val in signatures.items():
        statement_code += "<div class='col-4'>"
        
        statement_code += "<b>" + key + "</b>"
        
        sig_items = []
        for sig, occurs in val.items():
            sig_items.append([sig, occurs])
        sig_items.sort(key=lambda x: x[1], reverse=True)
        for sig, occurences in sig_items:
            statement_code += f"<div> {sig} - {occurences} </div>"
        statement_code += "</div><hr class='hr' />"
    
    
    html_code = f"""<head>{BOOTSTRAP_BOILERPLATE}</head><body>{statement_code}</body>"""
    
    html_file = open(f"html_parsing/predicates/identifiers_per_predicate.html", "w+")
    html_file.write(html_code)
    html_file.close()

def argument_ids_per_predicate_to_html():
    root = get_legal_ml_root("rioKB_GDPR.xml")
    gdpr = get_gdpr(root).get_articles()
    
    rule_tree_utils = []
    article_queue = [gdpr]
    while len(article_queue) > 0:
        curr_paragraph = article_queue.pop(0)
        for key, article_content in curr_paragraph.items():
            if key == "statements":
                for statement in article_content:
                    rule_tree_utils.append(RuleTreesUtil(statement[0]))
            else:
                article_queue.append(article_content)
    
    signatures = {}
    while len(rule_tree_utils) > 0:
        curr_tree_util = rule_tree_utils.pop(0)
        trees = curr_tree_util.if_trees.copy()
        for then_tree in curr_tree_util.then_trees:
            trees.append(then_tree)
        [clean_tree(x) for x in trees]
        
        """for tree in trees:
            queue = [tree]
            while len(queue) > 0:
                curr = queue.pop()
                for i in range(len(curr.relations)):
                    child = curr.relations[i]
                    if child.parent_relation != curr.parent_relation:
                        continue
                    for j in range(len(child.relations)):
                        childs_child = child.relations[j]
                        if child.var == childs_child.var:
                            curr.relations[i] = childs_child
        
                    queue.append(child)
        """
        while len(trees) > 0:
            curr_tree = trees.pop(0)
            
            if not isinstance(curr_tree.parent_relation, Atom):
                continue
            
            relation_name = curr_tree.parent_relation.get_atom_content()[0].get_rel_name()
            if relation_name not in signatures:
                signatures[relation_name] = {}
            
            for i in range(len(curr_tree.relations)):
                child = curr_tree.relations[i]
                if child.parent_relation == curr_tree.parent_relation and len(child.relations) == 1:
                    trees.append(child.relations[0])
                else:
                    trees.append(child)
                    
            rel_identifior = tuple([str(x) for x in curr_tree.parent_relation.get_atom_content()[0].get_rel_content()])

            if rel_identifior in signatures[relation_name]:
                signatures[relation_name][rel_identifior] += 1
            else:
                signatures[relation_name][rel_identifior] = 1
            
    for key, val in signatures.items():
        print(f"key: {key}: num_sigs: {len(val)}")

    statement_code = "<div class='container-fluid'>"
    statement_code += "<div class='row'>"
    
    for key, val in signatures.items():
        statement_code += "<div class='col-4'>"
        
        statement_code += "<b>" + key + "</b>"
        
        sig_items = []
        for sig, occurs in val.items():
            sig_items.append([sig, occurs])
        sig_items.sort(key=lambda x: x[1], reverse=True)
        for sig, occurences in sig_items:
            statement_code += f"<div> {sig} - {occurences} </div>"
        statement_code += "</div><hr class='hr' />"
    
    
    html_code = f"""<head>{BOOTSTRAP_BOILERPLATE}</head><body>{statement_code}</body>"""
    
    html_file = open(f"html_parsing/predicates/argument_identificators_per_predicate.html", "w+")
    html_file.write(html_code)
    html_file.close()


def make_per_argument_val():
    root = get_legal_ml_root("rioKB_GDPR.xml")
    gdpr = get_gdpr(root).get_articles()
    
    all_rules = []
    article_queue = [gdpr]
    while len(article_queue) > 0:
        curr_paragraph = article_queue.pop(0)
        for key, article_content in curr_paragraph.items():
            if key == "statements":
                for statement in article_content:
                    all_rules.append(statement[0])
            else:
                article_queue.append(article_content)
        
    arguments_per_predicate = {} 
           
    for rule in all_rules:
        rule_mapping = {}
        all_predicates = []
        for predicate in rule.if_atoms + rule.then_atoms:
            if not isinstance(predicate.get_atom_content()[0], Relation) or len(predicate.get_atom_content()[0].get_rel_content()) == 0:
                continue
            all_predicates.append(predicate)
            id_val = str(predicate.get_atom_content()[0].get_rel_content()[0])
            pred_name = predicate.get_atom_content()[0].get_rel_name()
            if id_val not in rule_mapping:
                rule_mapping[id_val] = []
            if pred_name not in arguments_per_predicate:
                arguments_per_predicate[pred_name] = {}
            rule_mapping[id_val].append(pred_name)
        
        for predicate in all_predicates:
            start_index = 0
            if predicate.is_reified():
                start_index = 1
            for i in range(start_index, len(predicate.get_atom_content()[0].get_rel_content())):
                id_val = str(predicate.get_atom_content()[0].get_rel_content()[i])
                pred_name = predicate.get_atom_content()[0].get_rel_name()
                
                if i not in arguments_per_predicate[pred_name]:
                    arguments_per_predicate[pred_name][i] = {"total_seen" : 1}

                else:
                    arguments_per_predicate[pred_name][i]["total_seen"] += 1
                if id_val not in rule_mapping:
                    id_list = ["Unknown"]
                else:
                    id_list = rule_mapping[id_val]
                id_list_no_dup = []
                [id_list_no_dup.append(x) for x in id_list if x not in id_list_no_dup]
                for id in id_list_no_dup:
                    if id not in arguments_per_predicate[pred_name][i]:
                        arguments_per_predicate[pred_name][i][id] = 1
                    else:
                        arguments_per_predicate[pred_name][i][id] += 1
    
    
    statement_code = "<div class='container-fluid'>"

    for predicate_name in arguments_per_predicate:
        
        statement_code += '</br></br><div class="col-12">'
        statement_code += f"<b> {predicate_name} </b>"
        
        statement_code += "<div class='row'>"
        for arg_num in arguments_per_predicate[predicate_name]:
            total_seen = arguments_per_predicate[predicate_name][arg_num]["total_seen"]
            
            statement_code += "<div class='col-3'>"
            statement_code += f"<b> {predicate_name} - arg {arg_num} - tot {total_seen} </b>"
            
            argument_order = []
            for id_val in arguments_per_predicate[predicate_name][arg_num]:
                if id_val == "total_seen":
                    continue
                fraction = arguments_per_predicate[predicate_name][arg_num][id_val] / total_seen

                argument_order.append((id_val, fraction))
            
            # Order arguments by biggest to smallest fraction value
            argument_order.sort(key=lambda x: x[1], reverse=True)
            
            for argument in argument_order:
                statement_code += f"<div> {argument[0]} - {argument[1]} </div>"
            
            statement_code += "</div>"
        statement_code += "</div></div>"
    
    
    html_code = f"""<head>{BOOTSTRAP_BOILERPLATE}</head><body>{statement_code}</body>"""
    
    html_file = open(f"html_parsing/signatures/signatures_with_original_predicate_name.html", "w+")
    html_file.write(html_code)
    html_file.close()

def check_quantification_to_html():
    root = get_legal_ml_root("rioKB_GDPR_original.xml")
    gdpr = get_gdpr(root).get_articles()
    
    all_rules = []
    article_queue = [gdpr]
    while len(article_queue) > 0:
        curr_paragraph = article_queue.pop(0)
        for key, article_content in curr_paragraph.items():
            if key == "statements":
                for statement in article_content:
                    all_rules.append(statement[0])
            else:
                article_queue.append(article_content)

    # Find doubly existentially quantified
    errors = {}
    for rule in all_rules:
        if_exist = rule.if_exist
        then_exist = rule.then_exist
        
        intersection = []
        for var in if_exist:
            if var in then_exist:
                intersection.append(var)
        if len(intersection) > 0:
            print([str(x) for x in intersection])
            print(rule)
    
    int_err_count = 0
    if_err_count = 0
    then_err_count = 0
    for rule in all_rules:
        if_vars = []
        then_vars = []
        
        for atom in rule.if_atoms:
            for cont in atom.atom_content:
                if isinstance(cont, Var) and cont not in if_vars:
                    if_vars.append(cont)
                elif isinstance(cont, Before) or isinstance(cont, After):
                    if isinstance(cont.t1, Var) and cont.t1 not in if_vars:
                        if_vars.append(cont.t1)
                    if isinstance(cont.t2, Var) and cont.t2 not in if_vars:
                        if_vars.append(cont.t2)
                    if isinstance(cont.t1, Function) and cont.t1.arguments[0] not in if_vars:
                        if not isinstance(cont.t1.arguments[0], Var):
                            print("ERROR")
                            exit()
                        if_vars.append(cont.content)
                elif isinstance(cont, Relation):
                    for arg in cont.get_rel_content():
                        if isinstance(arg, Var) and arg not in if_vars:
                            if_vars.append(arg)
                        if isinstance(arg, Function):
                            for func_arg in arg.arguments:
                                if isinstance(func_arg, Var) and func_arg not in if_vars:
                                    if_vars.append(func_arg)
                else:
                    print(type(cont))
                        
        for atom in rule.then_atoms:
            for cont in atom.atom_content:
                if isinstance(cont, Var) and cont not in then_vars:
                    then_vars.append(cont)
                elif isinstance(cont, Before) or isinstance(cont, After):
                    if isinstance(cont.t1, Var) and cont.t1 not in then_vars:
                        then_vars.append(cont.t1)
                    if isinstance(cont.t2, Var) and cont.t2 not in then_vars:
                        then_vars.append(cont.t2)
                    if isinstance(cont.t1, Function) and cont.t1.arguments[0] not in then_vars:
                        if not isinstance(cont.t1.arguments[0], Var):
                            print("ERROR")
                            exit()
                        then_vars.append(cont.content)
                
                elif isinstance(cont, Relation):
                    for arg in cont.get_rel_content():
                        if isinstance(arg, Var) and arg not in then_vars:
                            then_vars.append(arg)
                        if isinstance(arg, Function):
                            for func_arg in arg.arguments:
                                if isinstance(func_arg, Var) and func_arg not in then_vars:
                                    then_vars.append(func_arg)
        intersection = []
        only_if = []
        only_then = []
        
        for var in if_vars:
            if var in then_vars:
                intersection.append(var)
        
        for var in if_vars:
            if var not in intersection:
                only_if.append(var)
        for var in then_vars:
            if var not in intersection:
                only_then.append(var)

        for var in intersection:
            if var in rule.if_exist or var in rule.then_exist:
                int_err_count += 1
                print(f"Intersection error in rule with id {var}:\n {rule}")
                
        for var in only_if:
            if var not in rule.if_exist:
                if_err_count += 1
                #print(f"Var only used in IF not existentially quantified with id {var}:\n {rule}")
        
        for var in only_then:
            if var not in rule.then_exist:
                then_err_count += 1
                print(f"Var only used in THEN not existentially quantified with id {var}:\n {rule}")

    print(f"Error counts\n Intersection errors: {int_err_count}\n IF errors: {if_err_count}\n THEN errors: {then_err_count}")
    
def complexity_of_model_to_html():
    root = get_legal_ml_root("rioKB_GDPR_original.xml")
    gdpr = get_gdpr(root).get_articles()
    
    all_rules = []
    article_queue = [gdpr]
    while len(article_queue) > 0:
        curr_paragraph = article_queue.pop(0)
        for key, article_content in curr_paragraph.items():
            if key == "statements":
                for statement in article_content:
                    all_rules.append(statement[0])
            else:
                article_queue.append(article_content)

    tot_pred_relations_pair = []
    tot_pred_most_referenced_item_pair = []
    avg_relations_pred_pair = []
    tot_preds_ids_pair = []
    all_vars = {}
    for rule in all_rules:
        all_vars.clear()
        if_and_then = rule.if_atoms + rule.then_atoms
        num_predicates = len(if_and_then)
        print(f"len: {num_predicates}")
        for atom in if_and_then:
            for cont in atom.atom_content:
                if isinstance(cont, Var):
                    if str(cont) in all_vars:
                        print(f"adding {cont}")
                        all_vars[str(cont)] += 1
                        print(all_vars[str(cont)])
                    else:
                        print(f"adding {cont}")
                        all_vars[str(cont)] = 1
                        print(all_vars[str(cont)])
                elif isinstance(cont, Before) or isinstance(cont, After):
                    t1_var = None
                    t2_var = None
                    if isinstance(cont.t1, Var):
                        t2_var = cont.t1
                    if isinstance(cont.t2, Var):
                        t2_var = cont.t2
                    if isinstance(cont.t1, Function):
                        t1_var = cont.t1.arguments[0]
                    
                    if t1_var is not None:
                        if str(t1_var) in all_vars:
                            print(f"adding {t1_var}")
                            all_vars[str(t1_var)] +=  1
                            print(all_vars[str(t1_var)])
                        else:
                            print(f"adding {t1_var}")
                            all_vars[str(t1_var)] = 1
                            print(all_vars[str(t1_var)])
                
                    if t2_var is not None:
                        if str(t2_var) in all_vars:
                            print(f"adding {t2_var}")
                            all_vars[str(t2_var)] += 1
                            print(all_vars[str(t2_var)])
                        else:
                            
                            print(f"adding {t2_var}")
                            all_vars[str(t2_var)] = 1
                            print(all_vars[str(t2_var)])
                            
                elif isinstance(cont, Relation):
                    for arg in cont.get_rel_content():
                        if isinstance(arg, Var):
                            if str(arg) in all_vars:
                                print(f"adding {arg}")
                                all_vars[str(arg)] += 1
                                
                                print(all_vars[str(arg)])
                            else:
                                print(f"adding {arg}")
                                all_vars[str(arg)] = 1
                                print(all_vars[str(arg)])
                                
                        elif isinstance(arg, Function):
                            for func_arg in arg.arguments:
                                if isinstance(func_arg, Var):
                                    if str(func_arg) in all_vars:
                                        all_vars[ str(func_arg)] +=  1
                                        print(f"adding {func_arg}")
                                        print(all_vars[str(func_arg)])
                                    else:
                                        print(f"adding {func_arg}")
                                        all_vars[ str(func_arg)] = 1
                                        print(all_vars[str(func_arg)])
                else:
                    print(type(cont))
            

        tot_pred_most_referenced_item_pair.append((num_predicates, max([x for x in all_vars.values()])))
        tot_pred_relations_pair.append((num_predicates, sum([x for x in all_vars.values()])))
        avg_relations_pred_pair.append((num_predicates, sum([x for x in all_vars.values()])/len(all_vars)))
        tot_preds_ids_pair.append((num_predicates, len(all_vars)))
        all_vars.clear()

    x = np.array([x[0] for x in tot_pred_most_referenced_item_pair])
    y = np.array([x[1] for x in tot_pred_most_referenced_item_pair])
    
    #x = np.array([x[0] for x in avg_relations_pred_pair])
    #y = np.array([x[1] for x in avg_relations_pred_pair])
    
    #x = np.array([x[0] for x in tot_preds_ids_pair])
    #y = np.array([x[1] for x in tot_preds_ids_pair])
    
    x = np.array([x[0] for x in tot_pred_relations_pair])
    y = np.array([x[1] for x in tot_pred_relations_pair])
    a, b = np.polyfit(x, y, 1)
    curve = np.polyfit(x, y, 2)
    plt.scatter(x=x, y=y, label="Observed references and predicates")
    plt.plot(x, a*x+b, label= 'Best fit, y = ' + '{:.2f}'.format(b) + ' + {:.2f}'.format(a) + 'x')   
    plt.xlabel('x - Number of predicates')
    plt.ylabel('y - Total relations with identifiers')
    #plt.plot(range(0,max([x[0] for x in tot_pred_relations_pair])), np.polyval(curve, range(0,max([x[0] for x in tot_pred_relations_pair]))), label=f"Best fit, y = {round(curve[0],5)}*x^2 + {round(curve[1], 5)}*x + {round(curve[2], 5)}")
    #plt.text(1, 17, 'y = ' + '{:.2f}'.format(b) + ' + {:.2f}'.format(a) + 'x', size=14)
    
    plt.legend()
    plt.savefig("report/Figure_1.pdf")
    plt.show()
if __name__ == "__main__":
    make_gdpr_rules_to_html()
    #make_gdpr_temporal_rules_to_html()
    #make_predicate_signatures_to_html()
    #make_predicate_signatures_with_arg_name_to_html()
    #ids_per_predicate_to_html()
    #argument_ids_per_predicate_to_html()
    #make_per_argument_val()
    #check_quantification_to_html()
    #complexity_of_model_to_html()