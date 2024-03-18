"""This script exists to add universal quantifiers 
to the WhyEnf formulæ that did not get them. The original
script did not add them because it was not necessary at the time/they were implicit"""

import re
import os

def get_all_predicates(text: str):
    p = re.compile(r'([a-zA-Z0-9_]+)\(((\s?\w+,?)+)\)')
    match_re = p.findall(text)
    pred_name_set = set()
    for match in match_re:
        for match_group in match[1].split(", "):
            pred_name_set.add(match_group)
    return pred_name_set

def get_exists_predicates(text: str):
    match_re = re.findall(r'EXISTS\s(\w+)\s\.', text)
    pred_name_set = set()
    for match in match_re:
        for match_group in match.split(", "):
            pred_name_set.add(match_group)
    return pred_name_set

if __name__ == "__main__":
    walk_dir = "./whyenf_files_manual"
    for root, subdirs, files, in os.walk(walk_dir):
        for file in files:
            if not file.endswith(".mfotl") or file.endswith("_u.mfotl"):
                continue
            f = open(os.path.join(root,file), "r")
            #f = open("./whyenf_files_manual/GDPR:art_5/para_1/list_1/point_a/formula1.mfotl", "r")
            f_text = f.read()
            f.close()

            all_used_preds = get_all_predicates(f_text)
            all_exist_preds = get_exists_predicates(f_text)
            universal_preds = all_used_preds - all_exist_preds
            
            #print(f"uni: {universal_preds}\nexist: {all_exist_preds}\nall: {all_used_preds}\n\n")
            #continue
            new_text = " ".join(["FORALL " + x + " ." for x in universal_preds]) + " " + f_text
            f_new = open(os.path.join(root, file.split(".")[0] + "_u.mfotl"), "w+")
            f_new.write(new_text)
            f_new.close()