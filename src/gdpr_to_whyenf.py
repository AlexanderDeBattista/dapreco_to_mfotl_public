import os
from util.legal_ml_parser import get_legal_ml_root, get_gdpr
import pipeline

def rec_evaluate_for_whyenf(gdpr: dict, path: str):
    rules_here = gdpr["statements"]
    if not os.path.exists(path):
        os.makedirs(path)
    print(path)
    create_whyenf_files(rules_here, path)

    for key, val in gdpr.items():
        if key == "statements": continue
        new_path = path + key + "/"
        rec_evaluate_for_whyenf(val, new_path)
    
def create_whyenf_files(staements: list, path: str):
    for statement in staements:
        formula_num = statement[1].split("Formula")[1]
        formula_path = path + "formula" + formula_num
        flat_tree = pipeline.temporal_rule_to_tree_pipeline(statement[0])
        mfotl_formula = flat_tree.get_printable_tree_with_duplicates()
        mfotl_formula = mfotl_formula.replace(":","_")
        
        whyenf_sig = flat_tree.get_whyenf_sig()
        # Replace predicate : (colon) with _ (underscore) on every line
        for i in range(len(whyenf_sig)):
            if whyenf_sig[i] == ":" and not (whyenf_sig[i+1:i+1+len("string")] == "string"):
                whyenf_sig = whyenf_sig[:i] + "_" + whyenf_sig[i+1:]
        

        f = open(formula_path+".mfotl", "w+")
        f.write(mfotl_formula)
        f.close()
        
        f = open(formula_path+".sig", "w+")
        f.write(whyenf_sig)
        f.close()
        

if __name__ == "__main__":
    root = get_legal_ml_root("rioKB_GDPR.xml")
    gdpr = get_gdpr(root)
    gdpr_dict = gdpr.get_articles()
    gdpr_dict["statements"] = []
    path = "./whyenf_files/"
    rec_evaluate_for_whyenf(gdpr_dict, path)