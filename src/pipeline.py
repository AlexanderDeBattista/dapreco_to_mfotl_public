from rule.rule import Rule
from atomic_concepts.atom import Atom, Relation
from util.legal_ml_parser import get_legal_ml_root, get_rules_for_statement, get_gdpr
from util.tree_from_rule.tree_from_rule import RuleTreesUtil
#from util.temporal.extract_strictly_temporal import remove_reification_for_rexist_and, remove_unreified_or, remove_unreified_not
from util.tree_modification.remove_reification import remove_temporal_reification, remove_unreified_or, remove_unreified_not, remove_unreified_and
from util.tree_modification.flatten_tree import flatten_tree, rewrite_non_delayed, remove_redundant_predicates, rewrite_functions, remove_duplicate_predicates
from pattern.flat_pattern.patterns import consent
from data_structure.rule_tree.rule_tree import RuleTree
from util.transform_temporal_structure.transform import transform_temporal_rule_structure
from data_structure.rule_graph.rule_graph import rule_to_temporal_tree
from data_structure.rule_tree.branch_modifier import Implies, And

def rule_to_tree_pipeline(rule: Rule) -> RuleTree:
    rule_trees = RuleTreesUtil(rule)

    #if rule_trees.is_disconnected():
    #print(rule_without_unreified_or)
    remove_temporal_reification(rule_trees.entire_rule_tree)
    #print(rule_trees.entire_rule_tree.printNTree())
    remove_unreified_or(rule_trees.entire_rule_tree)
    #print(rule_trees.entire_rule_tree.printNTree())
    remove_unreified_not(rule_trees.entire_rule_tree)
    #print(rule_trees.entire_rule_tree.printNTree())
    remove_unreified_and(rule_trees.entire_rule_tree)
    #print(rule_trees.entire_rule_tree.printNTree())
    temporal_tree = rule_to_temporal_tree(rule)
    
    print(temporal_tree.printNTree())
    
        
        
        
        
    return rule_trees.entire_rule_tree

def temporal_rule_to_tree_pipeline(rule: Rule) -> RuleTree:
    # With the nested temporal tree, we want to flatten its
    flat_rule_tree = RuleTreesUtil(rule)
    flat_non_temporal_tree = flat_rule_tree.entire_rule_tree
    temporal_tree = transform_temporal_rule_structure(rule)
    flat_tree = flatten_tree(temporal_tree)
    print(flat_tree.printNTree())
    flat_tree = remove_redundant_predicates(flat_tree)
    flat_tree = rewrite_functions(flat_tree)

    # Ugly edge-case handling, in cases where there is no temporal identificator in the consequent of an implication
    # which can lead the consequent part to be left out. This puts whatever existed in the left out consequent part, back in
    if isinstance(flat_non_temporal_tree.parent_relation, Implies) and flat_tree.parent_relation is None:
        new_root = RuleTree(None, Implies())
        new_root.add_node(flat_tree)
        new_root.add_node(flat_non_temporal_tree.relations[1])
        [new_root.relations[1].add_exists_var(x) for x in flat_rule_tree.then_exists]
        flat_tree = new_root

    # Sometimes not all leaf nodes are included in the consequent if the have already been included in the antecedent
    # Check if this is the case, by checking if any predicates defined in the consequent part of the expression does
    # not appear there. If so, add them to the consequent part.    
    if isinstance(flat_tree.parent_relation, Implies):
        and_queue = []
        root_and = None
        all_imply_children = []
        
        # Find the uppermost "and" node, because we eventually want to add the missing predicates to this node
        if isinstance(flat_tree.relations[1].parent_relation, And):
            root_and = flat_tree.relations[1]
            and_queue = [root_and]
        elif len(flat_tree.relations[1].relations) > 0 and isinstance(flat_tree.relations[1].relations[0].parent_relation, And):
            root_and = flat_tree.relations[1].relations[0]
            and_queue = [root_and]
        
        # Collect all predicates that exist under root and
        while len(and_queue) > 0:
            curr = and_queue.pop(0)
            for child in curr.relations:
                if isinstance(child.parent_relation, Atom):
                    all_imply_children.append(child.parent_relation)
                and_queue.append(child)
        
        # Check if any predicates defined in the consequent part is missing from the tree.
        # If it is missing, add it to the root and node
        if root_and is not None:
            for then_atom in rule.then_atoms:
                if isinstance(then_atom.get_atom_content()[0], Relation) and then_atom not in all_imply_children:
                    root_and.add_node(RuleTree(then_atom.get_atom_content()[0].get_rel_content()[0], then_atom))
    
    flat_tree = rewrite_non_delayed(flat_tree)
    
    flat_tree = remove_duplicate_predicates(flat_tree)
    return flat_tree

if __name__ == "__main__":
    root = get_legal_ml_root("rioKB_GDPR.xml")
    rules = get_rules_for_statement("statements49", root)
    rule = rules[0]
    
    #print(rule_to_tree_pipeline(rule).printNTree())
    tree = temporal_rule_to_tree_pipeline(rule)
    print(tree.printNTree())
    print(tree.get_printable_tree_with_duplicates())