from atomic_concepts import Atom, Var, Relation, Expression, Function
from atomic_concepts.interfaces import AtomContent

def parse_function_str(function: str):
    """Expects a string of the form 'fun(swrlb:add(t1, 1M))'

    Args:
        function (str): _description_

    Returns:
        [type]: _description_
    """
    search_str = "fun("
    assert function[:len(search_str)] == search_str
    assert function[-2:] == "))"
    function = function[len(search_str):-2]
    split_function = function.split("(")
    fun_name = split_function[0]
    arguments = split_function[1].split(", ")
    return Expression(Function(fun_name, [Var(":" + x) for x in arguments]))

def text_to_list_of_vars(relation_content: str) -> [AtomContent]:
    """Expects a string of the form 'a1, ep, er, fun(swrlb:add(t1, 1M)), b2'

    Args:
        relation_content (str): _description_

    Returns:
        [AtomContent]: _description_
    """
    
    parts_of_relation = relation_content.split(", ")
    if parts_of_relation[0] == "":
        return []
    processed_parts_of_relation = []
    search_str = "fun("
    i = 0
    while i < len(parts_of_relation):
        if parts_of_relation[i][:len(search_str)] == search_str:
            for j in range(i+1, len(parts_of_relation)):
                if parts_of_relation[j][-2:] == "))":
                    new_str = ", ".join(parts_of_relation[i:j+1])
                    processed_parts_of_relation.append(new_str)
                    i = j + 1
                    break
        else:
            processed_parts_of_relation.append(parts_of_relation[i])
            i += 1
    parsed_values = []
    for item in processed_parts_of_relation:
        if item[:len(search_str)] == search_str:
            parsed_values.append(parse_function_str(item))
        else:
            parsed_values.append(Var(":" + item))
    return parsed_values
    

def text_to_list_of_atoms(text: str) -> [Atom]:
    split_text = text.split(" AND ")
    parsed_expression = []
    for item in split_text:
        
        first_namespace = -1
        for i in range(len(item)):
            if item[i] == ":":
                first_namespace = i
                break
        split_atom = [item[:first_namespace], item[first_namespace+1:]]
        if len(split_atom) <= 1:
            raise Exception(f"Could not parse atom {item}")
        
        ontology = None
        if split_atom[0] == "rioOnto":
            ontology =  "rioOnto"
        elif split_atom[0] == "dapreco":
            ontology =  "dapreco"
        elif split_atom[0] == "prOnto":
            ontology = "prOnto"
        else:
            raise Exception(f"Unknown ontology {item[0]}")

        is_reified = False
        for i in range(len(split_atom[1])):
            if split_atom[1][i] == "(":
                split_atom.append(split_atom[1][i+1:-1])
                is_reified = (split_atom[1][i-1] == "'")
                if is_reified: split_atom[1] = split_atom[1][:i-1]
                else: split_atom[1] = split_atom[1][:i]
                break
    
        parsed_relation_content = text_to_list_of_vars(split_atom[2])
        new_atom = Atom(is_reified)
        new_relation = Relation(ontology + ":" + split_atom[1])
        new_relation.update_content(parsed_relation_content)
        new_atom.add_rel(new_relation)

        parsed_expression.append(new_atom)
    return parsed_expression