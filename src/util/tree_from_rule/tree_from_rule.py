from rule.rule import Rule
from util.tree_modification.clean_tree import clean_tree
from util.temporal.extract_strictly_temporal import get_vars_this_var_defines
from util.legal_ml_parser.legal_ml_parser import get_legal_ml_root, get_rules_for_statement
from atomic_concepts.interfaces import AtomIterable, AtomContent
from atomic_concepts import Relation, Var, Atom
from name_space.name_space import NameSpace
from data_structure.rule_tree.rule_tree import RuleTree
from data_structure.rule_tree.branch_modifier import And, Or, Not, Implies, BranchModifier


class RuleTreesUtil():
    
    def __init__(self, rule: Rule) -> None:
        self.if_exists = rule.if_exist
        self.then_exists = rule.then_exist
        self.if_trees = []
        self.then_trees = []
        self.only_in_if_trees = []
        self.only_in_then_trees = []
        self.entire_rule_tree = None
        self.rule = rule
        self._parse_rule_to_get_temporal(rule)
        self._parse_entire_rule(rule)
        
    def get_exist_at_time(self, predicates: [AtomContent]):
        exist_at_time = []
        atom_list = predicates.copy()
        while len(atom_list) > 0:
            curr = atom_list.pop(0)
            if isinstance(curr, AtomIterable):
                for sub_item in curr:
                    atom_list.append(sub_item)
            if isinstance(curr, Atom):
                if not isinstance(curr.get_atom_content()[0], Relation):
                    continue
                if curr.get_atom_content()[0].get_rel_name() == (NameSpace.RIOONTO.value + ":RexistAtTime"):
                    exist_at_time.append(curr)
                if curr.get_atom_content()[0].get_rel_name() in [(NameSpace.RIOONTO.value+ ":Obliged"), (NameSpace.RIOONTO.value+ ":Permitted")] and not curr.is_reified():
                    exist_at_time.append(curr)
        return exist_at_time
    
    def _parse_entire_rule(self, rule: Rule):
        self.entire_rule_tree = RuleTree(Implies(), Implies())
        if_and_tree = RuleTree(And(), None, exists_var=rule.if_exist)
        [if_and_tree.add_node(RuleTree(None, x)) for x in rule.if_atoms]
        then_and_tree = RuleTree(And(), None, exists_var=rule.then_exist)
        [then_and_tree.add_node(RuleTree(None, x)) for x in rule.then_atoms]
        
        
        self.entire_rule_tree.add_node(if_and_tree)
        self.entire_rule_tree.add_node(then_and_tree)
        
    def _parse_rule_to_get_temporal(self, rule: Rule):
            
        if_and_then_atoms = rule.if_atoms.copy()
        for atom in rule.then_atoms:
            if_and_then_atoms.append(atom)
            
        if_exist_at_time = self.get_exist_at_time(rule.if_atoms.copy())
        then_exist_at_time = self.get_exist_at_time(rule.then_atoms.copy())
        for exist_item in if_exist_at_time:
            var_connected_to_time = exist_item.get_atom_content()[0].get_rel_content()[0] #a1, a2,...
            #time_variable = exist_item.atom_content[0].get_rel_content()[1] # t1, t2,...
            curr_tree = RuleTree(var_connected_to_time, exist_item)
            self.if_trees.append(curr_tree)
            
            curr_if_only_tree = RuleTree(var_connected_to_time, exist_item)
            self.only_in_if_trees.append(curr_if_only_tree)

            #self.append_vars_this_var_defines(var_connected_to_time, exist_item, if_and_then_atoms.copy(), curr_tree, [], [])
            self.append_vars_this_var_defines(var_connected_to_time, exist_item, rule.if_atoms.copy(), curr_tree, [], [])
            self.append_vars_this_var_defines(var_connected_to_time, exist_item, rule.if_atoms.copy(), curr_if_only_tree, [], [])
        for exist_item in then_exist_at_time:
            
            var_connected_to_time = exist_item.get_atom_content()[0].get_rel_content()[0] #a1, a2,...
            time_variable = exist_item.atom_content[0].get_rel_content()[1] # t1, t2,...
            curr_tree = RuleTree(var_connected_to_time, exist_item)
        
            self.then_trees.append(curr_tree)

            curr_then_only_tree = RuleTree(var_connected_to_time, exist_item)
            self.only_in_then_trees.append(curr_then_only_tree)

   
            #self.append_vars_this_var_defines(var_connected_to_time, exist_item, if_and_then_atoms.copy(), curr_tree, [], [])
            self.append_vars_this_var_defines(var_connected_to_time, exist_item, rule.then_atoms.copy(), curr_tree, [], [])
            self.append_vars_this_var_defines(var_connected_to_time, exist_item, rule.then_atoms.copy(), curr_then_only_tree, [], [])

    # TODO: Optimize this function, it is n^2, and it shows
    def append_vars_this_var_defines(self, var: Var, atom: Atom, rule: [AtomContent], parent_tree: RuleTree, already_tracked: [Var], already_tracked_atom: [Atom]):
            if parent_tree.is_leaf():
                return
            vars_to_track = []
            atoms_to_track = []
            already_tracked.append(var)
            already_tracked_atom.append(atom)
            get_vars_this_var_defines(rule, var, vars_to_track, atoms_to_track, already_tracked, already_tracked_atom)
            for i in range(len(vars_to_track)):
                curr_var = vars_to_track[i]
                curr_atom = atoms_to_track[i]
                curr_tree = RuleTree(curr_var, curr_atom)
                parent_tree.add_node(curr_tree)
               
                # Assume that relations with only one argument, is a leaf node
                if (isinstance(curr_atom, Atom) and len(curr_atom.get_atom_content()[0].get_rel_content()) == 1):
                    curr_tree.set_is_leaf()
                self.append_vars_this_var_defines(curr_var, curr_atom, rule, curr_tree, already_tracked, already_tracked_atom)
            # Define the leaf nodes of the tree (Usually they define some concept)

            already_tracked.pop()
            already_tracked_atom.pop()
    
    def number_of_trees(self):
        return (len(self.if_trees) + len(self.then_trees))
    
    def is_disconnected(self):
        if self.number_of_trees == 1:
            return True
        
        reified_vars_in_trees = []
        all_trees = self.if_trees.copy()
        [all_trees.append(x) for x in self.then_trees]
        for tree in all_trees:
            reified_vars = [] # TODO: Maybe change this name to something appropriate? We include all reified variables AND time identificators (a1, a2, t1, t2, etc)
            queue = tree.relations.copy()
            # TODO: Right now only reified identifiers/vars are included (as well as a1, a2,...,etc) - 
            #  do we want to include non-reified variables that are not leaf nodes as well?
            while len(queue) > 0:
                curr = queue.pop(0)
                if curr.parent_relation.is_reified():
                    reified_vars.append(curr.parent_relation.get_atom_content()[0].get_rel_content()[0])
                if curr.parent_relation.get_atom_content()[0].get_rel_name() == (NameSpace.RIOONTO.value + ":RexistAtTime"):
                    reified_vars.append(curr.parent_relation.get_atom_content()[0].get_rel_content()[0])
                for rel in curr.relations:
                    queue.append(rel)

            # Remove duplicates
            reified_vars_in_trees.append(set(reified_vars))
        
        for i in range(len(reified_vars_in_trees)):
            for j in range(i+1, len(reified_vars_in_trees)):
                intersect = set(reified_vars_in_trees[i]).intersection(set(reified_vars_in_trees[j]))
                if len(intersect) > 0:
                    print(f"Trees {i} and {j} are connected by reified variables {[str(x) for x in intersect]}")
                    return False
        
        return True
        
    
    def print_as_expression(self):
        if_items = []
        queue = self.only_in_if_trees.copy()
        while len(queue) > 0:
            curr = queue.pop()
            for subtree in curr.relations:
                queue.append(subtree)
            if curr.parent_relation not in if_items:
                if_items.append(curr.parent_relation)
        
        then_items = []
        queue = self.only_in_then_trees.copy()
        while len(queue) > 0:
            curr = queue.pop()
            for subtree in curr.relations:
                queue.append(subtree)
            if curr.parent_relation not in then_items:
                then_items.append(curr.parent_relation)
    
if __name__ == "__main__":
    root = get_legal_ml_root('rioKB_GDPR.xml')
    #rules = get_rules_for_statement("statements44", root)
    rules = get_rules_for_statement("statements83", root)
    rule_trees = RuleTreesUtil(rules[0])
    
    rule_trees.print_as_expression()
    clean_tree(rule_trees.then_trees[0])
    print(rule_trees.then_trees[0].printNTree())