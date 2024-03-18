import os

path = os.getcwd() + "/whyenf_files_manual"
seen_preds = {"cau" : {}, "sup": {}, "obs": {}}
seen_preds_with_args = {}
seen_preds_2 = {}
already_processed = set()


def handle_signature_file_2(path, seen_preds, seen_preds_with_args):
    sig_file = open(path, "r")
    sig_file_lines = sig_file.readlines()
    for line in sig_file_lines:
        line = line.strip()
        pred_name = line.split("(")[0]
        end = line[-2:]
        if pred_name in seen_preds:
            continue
        seen_preds_with_args[line] = True
        seen_preds[pred_name] = True
        
def handle_signature_file(path, seen_preds):
    sig_file = open(path, "r")
    sig_file_lines = sig_file.readlines()
    for line in sig_file_lines:
        line = line.strip()
        pred_name = line.split("(")[0]
        end = line[-2:]
        if "+" in end:
            if pred_name not in seen_preds["cau"]:
                seen_preds["cau"][pred_name] = 0
            seen_preds["cau"][pred_name] += 1

        if "-" in end:
            if pred_name not in seen_preds["sup"]:
                seen_preds["sup"][pred_name] = 0
            seen_preds["sup"][pred_name] += 1
        
        if "+" not in end and "-" not in end:
            if pred_name not in seen_preds["obs"]:
                seen_preds["obs"][pred_name] = 0
            seen_preds["obs"][pred_name] += 1
        
def iterate_folders_2(path, seen_preds, seen_preds_with_args, already_processed):
    for root, subdirs, files in os.walk(path):
        for file in files:
            if file.endswith(".sig"):
                path = os.path.join(root, file)
                if path not in already_processed:
                    already_processed.add(path)
                    handle_signature_file_2(os.path.join(root, file), seen_preds, seen_preds_with_args)
        
        for subdir in subdirs:
            iterate_folders_2(os.path.join(root, subdir), seen_preds, seen_preds_with_args, already_processed)
            
def iterate_folders(path, seen_preds, already_processed):
    for root, subdirs, files in os.walk(path):
        for file in files:
            if file.endswith(".sig"):
                path = os.path.join(root, file)
                if path not in already_processed:
                    already_processed.add(path)
                    handle_signature_file(os.path.join(root, file), seen_preds)
        
        for subdir in subdirs:
            iterate_folders(os.path.join(root, subdir), seen_preds, already_processed)

iterate_folders_2(path, seen_preds_2, seen_preds_with_args, already_processed)
print(seen_preds_with_args.keys())
"""
iterate_folders(path, seen_preds, already_processed)
print(seen_preds["cau"].keys())
print(seen_preds["sup"].keys())
print(list(set(seen_preds["cau"].keys()) & set(seen_preds["sup"].keys())))
"""