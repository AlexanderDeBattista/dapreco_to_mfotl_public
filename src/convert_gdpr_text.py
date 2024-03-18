import json

gdpr_text = json.load(open("html_parsing/gdpr_en.json", "r"))
new_gdpr_text = {}

for chapter, chapter_content in gdpr_text.items():
    if not isinstance(chapter_content, dict): continue
    weird_integer = "0"
    for weird_integer, weird_integer_val in chapter_content.items():
        if isinstance(weird_integer_val, str):
            continue
        
        for art, art_content in weird_integer_val.items():
            if isinstance(art_content, str):
                new_gdpr_text[art] = art_content
                continue
            if f"GDPR:art_{art}" not in new_gdpr_text:
                new_gdpr_text[f"GDPR:art_{art}"] = {}
            for para, para_content in art_content.items():
                
                if isinstance(para_content, str):
                    new_gdpr_text[f"GDPR:art_{art}"][para] = art_content
                    continue
                    
                #if art == "12":
                #    print(new_gdpr_text[f"GDPR:art_{art}"])
                
                if f"para_{para}" not in new_gdpr_text[f"GDPR:art_{art}"]:
                    new_gdpr_text[f"GDPR:art_{art}"][f"para_{para}"] = {}
                
                for list_point, list_point_content in para_content.items():
                    if isinstance(list_point_content, str):
                        new_gdpr_text[f"GDPR:art_{art}"][f"para_{para}"][list_point] = list_point_content
                        continue
                    if list_point == "litterae":
                        new_gdpr_text[f"GDPR:art_{art}"][f"para_{para}"]["list_1"] = {}
                        if isinstance(list_point_content, str):
                            new_gdpr_text[f"GDPR:art_{art}"][f"para_{para}"][list_point] = art_content
                            continue
                        for point in list_point_content:
                            new_gdpr_text[f"GDPR:art_{art}"][f"para_{para}"]["list_1"][f"point_{point}"] = list_point_content[point]

json.dump(new_gdpr_text, open("html_parsing/parsed_gdpr_en.json", "w"))
#for key, value in new_gdpr_text.items():
#    print(key)
#print(gdpr_text["6"]["0"]["1"])