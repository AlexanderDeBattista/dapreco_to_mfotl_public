from data_structure.rule_graph.rule_graph import rule_to_temporal_tree
from data_structure.rule_tree.rule_tree import RuleTree
from atomic_concepts import Atom
from util.tree_from_rule.tree_from_rule import RuleTreesUtil
from rule.rule import Rule
from atomic_concepts import Var
from util.legal_ml_parser.legal_ml_parser import get_rules_for_statement, get_legal_ml_root
from util.tree_modification.remove_reification import remove_unreified_and_temporal_tree, remove_unreified_not_temporal_tree, remove_unreified_or_temporal_tree, remove_unreified_implies_temporal_tree
from data_structure.rule_tree.branch_modifier import Implies
from util.tree_modification.clean_tree import clean_tree
from name_space.name_space import NameSpace

def find_subtree_defined_by_var(tree: RuleTree, var: Var):
    res = []
    queue = [tree]
    while len(queue) > 0:
        curr = queue.pop(0)
        if curr.var == var:
            res.append(curr)
        for child in curr.relations:
            queue.append(child)
    if len(res) == 0:
        raise Exception(f"Var, {var}, not found in tree {tree.printNTree()}")
    return res

def transform_temporal_rule_structure(rule: Rule) -> RuleTree:
    
    temporal_tree = rule_to_temporal_tree(rule)
    rule_tree = RuleTreesUtil(rule)
    queue = rule_tree.if_trees.copy()
    for tree in rule_tree.then_trees:
        queue.append(tree)
    while len(queue) > 0:
        curr = queue.pop()
        matching_temporal_trees = find_subtree_defined_by_var(temporal_tree, curr.var)
        for matching_tree in matching_temporal_trees:
            and_child = []
            matching_tree.exists_var = curr.exists_var
            for child in curr.relations:
                # Add the children that are not "and" to the matching tree
                # We want to add a separate "and" tree for the and predicate
                if isinstance(child.parent_relation, Atom) and child.parent_relation.get_atom_content()[0].get_rel_name() in [NameSpace.RIOONTO.value+":and", NameSpace.RIOONTO.value+":or", NameSpace.RIOONTO.value+":not", NameSpace.RIOONTO.value+":imply"]:
                    and_child.append(child)
                else:
                    matching_tree.add_node(child)
            # Add "and" children to the matching tree   
            if len(and_child) > 0:
                new_and_tree = RuleTree(curr.var, and_child[0].parent_relation)
                for child in and_child:
                    new_and_tree.add_node(child)
                matching_tree.add_node(new_and_tree)
    clean_tree(temporal_tree)
    if isinstance(temporal_tree.parent_relation, Implies):
        [temporal_tree.relations[0].add_exists_var(x) for x in rule_tree.if_exists]
        [temporal_tree.relations[1].add_exists_var(x) for x in rule_tree.then_exists]
    else:
        [temporal_tree.add_exists_var(x) for x in rule_tree.if_exists]
    remove_unreified_and_temporal_tree(temporal_tree)
    remove_unreified_not_temporal_tree(temporal_tree)
    remove_unreified_or_temporal_tree(temporal_tree)
    remove_unreified_implies_temporal_tree(temporal_tree)
    #print(tmp)
    return temporal_tree

if __name__ == '__main__':
    root = get_legal_ml_root("rioKB_GDPR.xml")
    rules = get_rules_for_statement("statements83", root)#("statements37", root)
    
    temporal_rule = transform_temporal_rule_structure(rules[0])
    print(temporal_rule.printNTree())
    print(temporal_rule.get_printable_flat_tree())