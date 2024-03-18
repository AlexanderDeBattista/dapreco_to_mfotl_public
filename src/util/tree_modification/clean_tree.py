from data_structure.rule_tree.rule_tree import RuleTree
from atomic_concepts import Atom, Var


def clean_tree(rule_tree: RuleTree):
    curr_parent = rule_tree.parent_relation
    curr_var = rule_tree.var
    
    # By only allowing a var in a tree to refer to a subtree containing its own var, or multiple subtrees none of which contains
    # the var, we remove a lot of noise.
    children = []
    for child_tree in rule_tree.relations:
        if not isinstance(curr_var, Var):
            continue
        if curr_var == child_tree.var:
            children.append(child_tree)
    
    new_children = []
    for i in range(len(children)):
        child = children[i]
        new_children.append(child)
    children = new_children
    if len(children) > 0:
        rule_tree.relations = [x for x in children]
    for child_tree in rule_tree.relations:
        clean_tree(child_tree)