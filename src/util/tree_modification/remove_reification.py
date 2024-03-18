from data_structure.rule_tree.rule_tree import RuleTree
from data_structure.rule_tree.branch_modifier import And, Or, Not, Implies, BranchModifier
from rule.logical_connectives import LogicalConnective
from atomic_concepts import Atom, Var, Relation
from name_space.name_space import NameSpace

def find_and_remove_tree_based_on_var(rule_tree: RuleTree, var: Var):
    if len(rule_tree.relations) == 0:
        return []
    
    removed_trees = []
    for sub_tree in rule_tree.relations:
        [removed_trees.append(x) for x in find_and_remove_tree_based_on_var(sub_tree, var)]
        
        atom = sub_tree.parent_relation
        if not isinstance(atom, Atom):
            continue
        relation = atom.get_atom_content()[0]
        if not isinstance(relation, Relation) or len(relation.get_rel_content()) == 0:
            continue
        
        if relation.get_rel_content()[0] == var:
            rule_tree.relations.remove(sub_tree)
            removed_trees.append(sub_tree)
    return removed_trees

def remove_temporal_reification(rule_tree: RuleTree):
    if len(rule_tree.relations) == 0:
        return
    
    exist_atom = None
    exist_relation = None
    and_atom = None
    and_relation = None
    
    for sub_tree in rule_tree.relations:
        atom = sub_tree.parent_relation
        if not isinstance(atom, Atom):
            continue
        if not isinstance(atom.get_atom_content()[0], Relation):
            continue
        relation = atom.get_atom_content()[0]
        if relation.get_rel_name() == (NameSpace.RIOONTO.value+":RexistAtTime"):
            exist_atom = atom
            exist_relation = sub_tree
        # Check that the "and"'s identifier matches the "rexist"'s identifier
        if exist_atom is None:
            continue
        if relation.get_rel_name() == (NameSpace.RIOONTO.value + ":and") and relation.get_rel_content()[0] == exist_atom.get_atom_content()[0].get_rel_content()[0]:
            and_atom = atom
            and_relation = sub_tree
            break

    
    if (exist_atom is None or and_atom is None):
        vars_to_remove = []
        [vars_to_remove.append(remove_temporal_reification(x)) for x in rule_tree.relations]
        for var in vars_to_remove:
            if var in rule_tree.exists_var:
                rule_tree.exists_var.remove(var)
        
        return vars_to_remove
    
    # TODO: Do we really want to remove the "rexist" and "and" from the tree?
    and_atom.un_reify()
    # Remove the "rexist" and "and" from the tree, because they are not needed in the unreified tree
    #rule_tree.relations.remove(exist_relation)
    #rule_tree.relations.remove(and_relation)
    and_vars = [x for x in and_atom.get_atom_content()[0].get_rel_content()[1:]]
    
    for sub_tree in rule_tree.relations:
        atom = sub_tree.parent_relation
        if not isinstance(atom, Atom):
            continue
        relation = atom.get_atom_content()[0]
        if not isinstance(relation, Relation):
            continue
            
        if len(relation.get_rel_content()) > 0 and relation.get_rel_content()[0] in and_vars:
            atom.un_reify()
            
    vars_to_remove = []
    
    #vars_to_remove.append(exist_atom.get_atom_content()[0].get_rel_content()[0])
    #vars_to_remove.append(exist_atom.get_atom_content()[0].get_rel_content()[1])
    
    for var in vars_to_remove:
            if var in rule_tree.exists_var:
                rule_tree.exists_var.remove(var)
    
    return vars_to_remove


def remove_unreified_connective(rule_tree: RuleTree, original_rule_tree: RuleTree, connective_str: str, connective_obj: BranchModifier):
    if len(rule_tree.relations) == 0:
        return []
    
    connective_relation = None
    connective_atom = None
    
    # First find all sub_trees that contain the predicate we are interestd in (e.g. "or", "not")
    # Extract the relation/subtree if we find a match
    for sub_tree in rule_tree.relations:
        atom = sub_tree.parent_relation
        if not isinstance(atom, Atom):# or atom.is_reified():
            continue
        if not isinstance(atom.get_atom_content()[0], Relation):
            continue
        relation = atom.get_atom_content()[0]
        if relation.get_rel_name() == (connective_str):
            connective_atom = atom
            connective_relation = sub_tree
            break
    
    # Did not find any matches, recursively search the subtrees to try to find a match
    if (connective_atom is None):
        vars_to_remove = []
        nested_list = []
        [nested_list.append(remove_unreified_connective(x, original_rule_tree, connective_str, connective_obj)) for x in rule_tree.relations]
        [vars_to_remove.append(vars) for sublist in nested_list for vars in sublist]
        for var in vars_to_remove:
            if var in rule_tree.exists_var:
                rule_tree.exists_var.remove(var)
        
        return vars_to_remove
    
    # Remove the identified predicate from the tree, and replace it with the equivilant logical connective
    rule_tree.relations.remove(connective_relation)
    new_connective_tree = RuleTree(None, connective_obj)
    # Add the new connective to the parent tree
    rule_tree.add_node(new_connective_tree)
    
    # The vars that are referenced to in a connective predicate, that point to some other predicate
    connective_vars = connective_atom.get_atom_content()[0].get_rel_content()[1:]

    sub_trees_based_on_vars = []
    double_list = []
    # For each variable that was referenced in the connective predicate, find the subtree that contains that variable
    # Since we might find several subtrees for one variable, we first find all subtrees for one variable, then extract it to the list to make it flat
    [double_list.append(find_and_remove_tree_based_on_var(original_rule_tree, y)) for y in connective_vars]
    [sub_trees_based_on_vars.append(x) for sublist in double_list for x in sublist]

    for sub_tree in sub_trees_based_on_vars:
        atom = sub_tree.parent_relation
        if isinstance(atom, Atom):
            atom.un_reify()

        new_connective_tree.add_node(sub_tree)
    
    # Want to remove the variable that defined the predicate
    vars_to_remove = [connective_atom.get_atom_content()[0].get_rel_content()[0]]
    
    for var in vars_to_remove:
            if var in rule_tree.exists_var:
                rule_tree.exists_var.remove(var)
    
    return vars_to_remove

def remove_unreified_not(rule_tree: RuleTree):
    return remove_unreified_connective(rule_tree, rule_tree, (NameSpace.RIOONTO.value + ":not"), Not())

def remove_unreified_or(rule_tree: RuleTree):
    return remove_unreified_connective(rule_tree, rule_tree, (NameSpace.RIOONTO.value + ":or"), Or())

def remove_unreified_and(rule_tree: RuleTree):
    return remove_unreified_connective(rule_tree, rule_tree, (NameSpace.RIOONTO.value + ":and"), And())

def remove_unreified_connective_temporal_tree(rule_tree: RuleTree, original_rule_tree: RuleTree, connective_str: str, connective_obj: BranchModifier):
    # Recursively look for the connective predicate in the tree
    for child_rel in rule_tree.relations:
        remove_unreified_connective_temporal_tree(child_rel, original_rule_tree, connective_str, connective_obj)
    matches = []
    
    # Iterate over the children of the tree, to look for the connective predicate
    for child_rel in rule_tree.relations:
        if not isinstance(child_rel.parent_relation, Atom):# or not child_rel.parent_relation.is_reified():
            continue
        if not child_rel.parent_relation.get_atom_content()[0].get_rel_name() == connective_str:
            continue
        if not child_rel.parent_relation.get_atom_content()[0].get_rel_content()[0] == child_rel.var:
            continue
        matches.append(child_rel)
    
    
    if len(matches) > 0:
        new_parent = RuleTree(rule_tree.var, connective_obj)
        rule_tree.add_node(new_parent)
        child_to_match = []
        # For each match (which is a subtree that contains the connective predicate),
        # find the subtrees that are children to the connective predicate
        for match in matches:
            tmp_list = []
            for child in match.relations:
                # Want to remove the tree that contains the variable that defines the connective, get the child instead
                # It also removes a lot of noise
                #if not match.parent_relation.is_reified():
                if isinstance(child.parent_relation, Atom):
                    child.parent_relation.un_reify()
                if isinstance(child.parent_relation, BranchModifier) or child.parent_relation.get_atom_content()[0].get_rel_content()[0] == match.var:
                    # If there are nested relations where the same predicate is used twice (Once to first define
                    # the identifier in the predicate, and in the next to show which identifier from the predicate
                    # is used in the following branch)
                    if child.parent_relation == match.parent_relation:
                        [tmp_list.append(x) for x in child.relations]
                        [x.parent_relation.un_reify() for x in child.relations if isinstance(x.parent_relation, Atom)]
                    else:
                        tmp_list.append(child)

            child_to_match.append(tmp_list)
            
        for match, child in zip(matches, child_to_match):
            rule_tree.relations.remove(match)
            for child_tree in child:
                if len(child_tree.relations) == 1 and child_tree.parent_relation == rule_tree.parent_relation:
                    new_parent.add_node(child_tree.relations[0])
                else:
                    new_parent.add_node(child_tree)
    
    #"""
    if isinstance(connective_obj, Implies) and len(matches) > 0:

        group_one = []
        group_two = []
        for child in new_parent.relations:
            if child.var == new_parent.relations[0].var:
                group_one.append(child)
            else:
                group_two.append(child)
        
        
        dummy_rel = Relation("InfSecOnto:dummy")
        dummy_rel.add_relation_content(Var(":BadFormula"))
        dummy_atom = Atom(False)
        dummy_atom.add_rel(dummy_rel)
        if len(group_one) == 0:
            group_one.append(RuleTree(None, dummy_atom))
        if len(group_two) == 0:
            group_two.append(RuleTree(None, dummy_atom))
        
        new_parent.relations = [RuleTree(None, And()), RuleTree(None, And())]
 
        new_parent.relations[0].relations = group_one
        new_parent.relations[1].relations = group_two
    #"""
        
    """
        for match in matches:
            rule_tree.relations.remove(match)
            new_parent.add_node(match)
        """
def remove_unreified_and_temporal_tree(rule_tree: RuleTree):
    return remove_unreified_connective_temporal_tree(rule_tree, rule_tree, (NameSpace.RIOONTO.value + ":and"), And())

def remove_unreified_not_temporal_tree(rule_tree: RuleTree):
    return remove_unreified_connective_temporal_tree(rule_tree, rule_tree, (NameSpace.RIOONTO.value + ":not"), Not())

def remove_unreified_or_temporal_tree(rule_tree: RuleTree):
    return remove_unreified_connective_temporal_tree(rule_tree, rule_tree, (NameSpace.RIOONTO.value + ":or"), Or())

def remove_unreified_implies_temporal_tree(rule_tree: RuleTree):
    return remove_unreified_connective_temporal_tree(rule_tree, rule_tree, (NameSpace.RIOONTO.value + ":imply"), Implies())
