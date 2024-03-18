ontologies = set()

dapreco = open("rioKB_GDPR.xml")
for line in dapreco.readlines():
    if '<ruleml:Rel iri="swrl' in line and not "exceptionCha" in line:
        ontologies.add(line.split('"')[1].split(":")[1])
dapreco.close()
dapreco = open("rioKB_GDPR.xml")
"""
functions_dap = set()
functions_other = set()
for line in dapreco.readlines():
    if '<ruleml:Fun iri="dapreco' in line:
        functions_dap.add(line.split('"')[1])
    elif '<ruleml:Fun iri="' in line:
        functions_other.add(line.split('"')[1])
"""

print(ontologies)
print(len(ontologies))
print(functions_dap)
print(len(functions_dap))
print(functions_other)
print(len(functions_other))