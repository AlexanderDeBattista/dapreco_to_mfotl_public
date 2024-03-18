from atomic_concepts.relation import Relation
from util.legal_ml_parser.legal_ml_parser import get_gdpr, get_legal_ml_root

import matplotlib.pyplot as plt

def make_per_argument_val():
    root = get_legal_ml_root("rioKB_GDPR.xml")
    gdpr = get_gdpr(root).get_articles()
    
    all_rules = []
    article_queue = [(gdpr, "")]
    curr_art = ""
    art_dict = {}
    while len(article_queue) > 0:
        curr_paragraph, curr_art = article_queue.pop(0)
        for key, article_content in curr_paragraph.items():
            if "GDPR:art_" in key:
                curr_art = key
                if curr_art not in art_dict:
                    art_dict[curr_art] = {"tot":1, "tot_err":0}
            if key == "statements":
                for statement in article_content:
                    all_rules.append((statement[0], curr_art))
                    art_dict[curr_art]["tot"] += 1
            else:
                article_queue.append((article_content, curr_art))
        
    arguments_per_predicate = {} 

    for rule in all_rules:
        rule, curr_art = rule
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
                    if "t" not in id_val:
                        art_dict[curr_art]["tot_err"] += 1
                else:
                    id_list = rule_mapping[id_val]
                id_list_no_dup = []
                [id_list_no_dup.append(x) for x in id_list if x not in id_list_no_dup]
                for id in id_list_no_dup:
                    if id not in arguments_per_predicate[pred_name][i]:
                        arguments_per_predicate[pred_name][i][id] = 1
                    else:
                        arguments_per_predicate[pred_name][i][id] += 1

    return art_dict

def repeated_exists():
    root = get_legal_ml_root("rioKB_GDPR.xml")
    gdpr = get_gdpr(root).get_articles()
    
    all_rules = []
    article_queue = [(gdpr, "")]
    curr_art = ""
    art_dict = {}
    while len(article_queue) > 0:
        curr_paragraph, curr_art = article_queue.pop(0)
        for key, article_content in curr_paragraph.items():
            if "GDPR:art_" in key:
                curr_art = key
                if curr_art not in art_dict:
                    art_dict[curr_art] = {"tot":1, "tot_err":0}
            if key == "statements":
                for statement in article_content:
                    all_rules.append((statement[0], curr_art))
                    art_dict[curr_art]["tot"] += 1
            else:
                article_queue.append((article_content, curr_art))
        
    arguments_per_predicate = {} 

    for rule in all_rules:
        rule, curr_art = rule
        
        intersection_ext = [x for x in rule.if_exist if x in rule.then_exist]
        if len(intersection_ext):
            print(intersection_ext[0])
            print(curr_art)
            
repeated_exists()
#exit()
art_dict = make_per_argument_val()
err_per_formula_per_article = {}
tot_forms = 0
tot_errs = 0
for key,val in art_dict.items():
    err_per_formula_per_article[key.split("_")[1]] = val["tot_err"] / val["tot"]
    tot_forms += val["tot"]
    tot_errs += val["tot_err"]


fig, ax = plt.subplots()
ax.bar(err_per_formula_per_article.keys(), err_per_formula_per_article.values())
ax.set_title("Avarage number of bad identifiers per formula, by GDPR article",fontsize=20)
ax.set_ylabel("Average bad identifiers per formula",fontsize=20)
ax.set_xlabel("GDPR article number",fontsize=20)

ax.set_yticks([0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4])
ax.yaxis.grid(True, linestyle='--', which='major',
                color='grey', alpha=.25)
ax.axhline(tot_errs/tot_forms, linestyle='--', linewidth=4, label=f"Average, {tot_errs/tot_forms}")

plt.legend(fontsize="20")
fig.set_size_inches(20, 10, forward=True)
plt.savefig("./report/bad_ids_per_formula.pdf", dpi=100)
plt.show()