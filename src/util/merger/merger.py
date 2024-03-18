from data_structure.rule_tree.rule_tree import RuleTree
from atomic_concepts import Atom, Relation, Var
from name_space.name_space import NameSpace
from data_structure.rule_tree.branch_modifier import BranchModifier
from util.tree_modification.clean_tree import clean_tree
from util.legal_ml_parser.legal_ml_parser import get_legal_ml_root, get_rules_for_statement
from util.tree_from_rule.tree_from_rule import RuleTreesUtil

def merge_pattern_in_tree(rule_tree: RuleTree, pattern: RuleTree, replace_with: RuleTree, original_pattern: RuleTree, mid_search: bool, first_time: bool):
    """Finds and replaces a pattern in a rule tree and replace it with another tree

    Args:
        rule_tree (RuleTree): A rule tree that will be searched, and modified on match
        pattern (RuleTree): A pattern to search for in the rule tree
        replace_with (RuleTree): If a match is found, this tree will replace the pattern
        original_pattern (RuleTree): Backup pattern, used to reset the pattern if a match is not found
        mid_search (bool): Are we in the middle of a search? If so, we should not replace the tree
        first_time (bool): Is this the first time we are searching? If so, we should not replace the tree

    Returns:
        _type_: _description_
    """    
    
    # We do not consider the two nodes we currently evaluate (rule_tree and pattern) to be equal, if one of these
    # conditions do hold
    if ((len(rule_tree.relations) != len(pattern.relations))
        or (type(rule_tree.parent_relation) != type(pattern.parent_relation))
        or (isinstance(rule_tree.parent_relation, Atom)
            and rule_tree.parent_relation.get_atom_content()[0].get_rel_name() != pattern.parent_relation.get_atom_content()[0].get_rel_name())
        or (isinstance(rule_tree.parent_relation, BranchModifier)
            and rule_tree.parent_relation != pattern.parent_relation)):
        
        if first_time:
            merge_pattern_in_tree(rule_tree, original_pattern, replace_with, original_pattern, False, False)
        else:
            for relation in rule_tree.relations:
                merge_pattern_in_tree(relation, original_pattern, replace_with, original_pattern, False, True)
        
        return -1
    
    if len(rule_tree.relations) == 0:
        return 1
    
    sum = 0
    for i in range(len(rule_tree.relations)):
        sum += merge_pattern_in_tree(rule_tree.relations[i], pattern.relations[i], replace_with, original_pattern, True, True)
        print(f"sum: {sum}")
    if sum == len(rule_tree.relations) and not mid_search:
        rule_tree.relations = replace_with.relations
        rule_tree.parent_relation = replace_with.parent_relation
        rule_tree.var = replace_with.var
        return -1
    elif sum == len(rule_tree.relations) and mid_search:
        return 1
    else:
        return -1

def get_personal_data_pattern() -> (RuleTree, RuleTree):
    """Return a pattern that matches a personal data statement, and a tree that can replace the pattern

    Args:
        RuleTree (_type_): _description_

    Returns:
        _type_: _description_
    """    
    var = Var(":w")
    parent_relation = Relation("prOnto:PersonalData")
    parent_atom = Atom(False)
    parent_atom.add_rel(parent_relation)
    root = RuleTree(var, parent_atom)
    
    child_relation = Relation("prOnto:PersonalData")
    child_atom = Atom(False)
    child_atom.add_rel(child_relation)
    child_tree = RuleTree(var, child_atom)
    
    childs_child_relation = Relation("prOnto:DataSubject")
    childs_child_atom = Atom(False)
    childs_child_atom.add_rel(childs_child_relation)
    childs_child_tree = RuleTree(var, childs_child_atom)
    
    child_tree.add_node(childs_child_tree)
    root.add_node(child_tree)
    
    user_id_var = Var(":UserId")
    new_relation = Relation("PersonalData")
    new_relation.add_relation_content(user_id_var)
    new_atom = Atom(False)
    new_atom.add_rel(new_relation)
    to_replace_tree = RuleTree(user_id_var, new_atom)
    
    return (root, to_replace_tree)

def get_personal_data_processing_pattern() -> (RuleTree, RuleTree):
        personal_data_pattern = get_personal_data_pattern()[0]
        
        root_var = Var(":ep")
        root_atom = Atom(False)
        root_rel = Relation("prOnto:PersonalDataProcessing")
        root_atom.add_rel(root_rel)
        root = RuleTree(root_var, root_atom)
        
        root_child_var = Var(":x")
        root_child_atom = Atom(False)
        root_child_rel = Relation("prOnto:PersonalDataProcessing")
        root_child_atom.add_rel(root_child_rel)
        root_child = RuleTree(root_child_var, root_child_atom)
        
        processor_var = Var(":x")
        processor_atom = Atom(False)
        processor_rel = Relation("prOnto:Processor")
        processor_atom.add_rel(processor_rel)
        processor_tree = RuleTree(processor_var, processor_atom)
        
        
        root_child_two = RuleTree(root_child_var, root_child_atom)
        
        root.add_node(root_child)
        root.add_node(root_child_two)
        root_child.add_node(processor_tree)
        root_child_two.add_node(personal_data_pattern)
        
        to_replace_var = Var(":dataToProcess")
        to_replace_atom = Atom(False)
        to_replace_rel = Relation("prOnto:PersonalDataProcessing")
        to_replace_rel.add_relation_content(to_replace_var)
        to_replace_atom.add_rel(to_replace_rel)
        
        
        
        to_replace_tree = RuleTree(to_replace_var, to_replace_atom)
        
        return(root, to_replace_tree)
        

        
        
if __name__ == "__main__":
    root = get_legal_ml_root("rioKB_GDPR.xml")
    rules = get_rules_for_statement("statements34", root)
    rule_as_tree = RuleTreesUtil(rules[0]).if_trees[0]
    clean_tree(rule_as_tree)
    
    pattern, to_replace = get_personal_data_processing_pattern()#get_personal_data_pattern()
    
    print(rule_as_tree.printNTree())
    """print(rule_as_tree.printNTree())
    merge_pattern_in_tree(rule_as_tree, pattern, to_replace, pattern, False, True)
    print(rule_as_tree.printNTree())
    print(rule_as_tree.get_printable_flat_tree())"""