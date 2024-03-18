from atomic_concepts import Var, Relation, Function, Expression, Atom
from atomic_concepts.interfaces import AtomContent, AtomIterable
from rule.rule import Rule
from name_space.name_space import NameSpace

import itertools
import copy
from util.text_parser import text_to_pattern

from util.legal_ml_parser import get_legal_ml_root, get_rules_for_statement

class Pattern:
    
    def __init__(self, pattern: [AtomContent], unchangable_vars: [Var]) -> None:
        self.pattern = pattern
        self.empty_var_mapping = self._create_empty_mapping()
        self.unchangable_vars = unchangable_vars
    
    def _create_empty_mapping (self) -> dict:
        mapping = {}
        queue = copy.deepcopy(self.pattern)
        while len(queue) > 0:
            item = queue.pop(0)
            if isinstance(item, AtomIterable):
                for sub_item in item:
                    queue.append(sub_item)
            elif isinstance(item, Var):
                mapping[item] = None
        return mapping
    
    
    def rule_if_contains_pattern(self, rule: Rule) -> bool:
        return self._list_contains_pattern(rule.if_atoms)
    def rule_then_contains_pattern(self, rule: Rule) -> bool:
        return self._list_contains_pattern(rule.then_atoms)
    def rule_contains_pattern(self, rule: Rule):
        if_then_atoms = rule.if_atoms + rule.then_atoms
        return self._list_contains_pattern(if_then_atoms)
        
    def _list_contains_pattern(self, items: [AtomContent]) -> bool:
        # TODO: Expand to also use then_rules
        level_rules = items.copy()
        mappings = None
        
      
        # Get potential mappings from the queue
        mappings = self._get_potential_mappings(level_rules)
        
        for key, value in mappings.items():
            # Did not manage to find a mapping between at least one variable in the pattern and the rule
            if len(value) == 0:
                continue
            
            #TODO: Implement for other levels, too
            break
                    
        keys, values = zip(*mappings.items())
        combination_reverse_dict = [dict(zip(keys, v)) for v in itertools.product(*values)]
        # Replace the vars in pattern with the values in mapping, and see if the resulting pattern exists in the rule   
        for reverse_dict in combination_reverse_dict:
            
            # TODO: Implement that the vars in pattern are replaced with the values in reverse_dict, and then do a check if all the atoms in modified pattern exist in rules
            queue = copy.deepcopy(self.pattern)
            modified_pattern = [x for x in queue]
            while len(queue) > 0:
                curr = queue.pop(0)
                if isinstance(curr, AtomIterable):
                    for sub_item in curr:
                        queue.append(sub_item)
                elif isinstance(curr, Var):
                    curr.var_val = reverse_dict[curr].var_val
            
            all_matching = True
            for modified_item in modified_pattern:
                if modified_item not in level_rules:
                    all_matching = False
                    break
            
            if all_matching:
                return True
        return False
            
    def _get_potential_mappings(self, level: [AtomContent]) -> dict:
        """Given all expression in a level, return a dict of all possible mappings between the vars in the pattern and the vars in the level

        Args:
            level (AtomContent]): A list of AtomContents that constitues a level in a rule

        Returns:
            dict: A dictionary with vars as keys, and a list of all possible vars that can be mapped to the key var as values
        """        
        
        all_combinations = []
        
        # TODO: Make this function more efficient
        # Create all possible permutations between the items in the level and the pattern
        for item in level:
            for pattern_item in self.pattern:
                all_combinations.append((item, pattern_item))
        
        # Create an empty mapping for all the vars that appear in the pattern
        # This will be used to later append all possible vars (that potentially has a different name) that can be mapped to the pattern var
        potential_mappings = copy.deepcopy(self.empty_var_mapping)
        for key in potential_mappings.keys():
            potential_mappings[key] = []
        
        # If the the item and pattern_item matches (i.e. their structure is identical, with the potential exception of VAR names), then add it as a potential mapping
        # We do this, because we want to allow for abstract patterns with vars that may have different names - it makes them more general and reusable.
        for item, pattern_item in all_combinations:
            # Iterate over all pattern an item combinations, and check if they match (i.e. identical structure, with the potential exception of VAR names)
            items_queue = [item]
            pattern_items_queue = [pattern_item]
            matching = True
            
            var_matches = []
            
            # See that the structure of the item and pattern_item is identical
            while len(items_queue) > 0:
                # Different length means that the structure is not identical
                if len(items_queue) != len(pattern_items_queue):
                    matching = False
                    break
                
                curr_item = items_queue.pop(0)
                curr_pattern_item = pattern_items_queue.pop(0)
                # Needs to have the same type
                if not isinstance(curr_item, type(curr_pattern_item)):
                    matching = False
                    break
                
                # Need to have matching names, if they are relations
                if isinstance(curr_item, Relation) and not (curr_item.get_rel_name() == curr_pattern_item.get_rel_name()):
                    matching = False
                    break
                
                # Add iterable items to the queue, for both items and patterns queue
                if isinstance(curr_item, AtomIterable):
                    for item_to_queue in curr_item:
                        items_queue.append(item_to_queue)
                    for pattern_item_to_queue in curr_pattern_item:
                        pattern_items_queue.append(pattern_item_to_queue)

                elif isinstance(curr_item, Var):
                        # The current var might be a var that cannot change name (i.e. t1), and hence, we need to check 
                        # that the current item var is not one of those that cannot change name. 
                        # If name cannot change, and this var has a different name, then not a match
                        if curr_pattern_item in self.unchangable_vars and not curr_item == curr_pattern_item:
                            matching = False
                            break
                        # Append the potential mapping to the var_match.
                        # This will be used later to create the potential_mappings dict, given the rest of the items match
                        var_matches.append((curr_pattern_item, curr_item))
            # If we escaped the while loop, then we need to check that both queues are empty, if not then the structure is not identical
            if len(pattern_items_queue) > 0 or len(items_queue) > 0:
                matching = False
            if not matching:
                continue
            # Map the potential mappings to the dictionary
            for pattern_var, item_var in var_matches:
                potential_mappings[pattern_var].append(item_var)
        
        # Remove duplicate entries in dict
        for key, value in potential_mappings.items():
            potential_mappings[key] = list(set(value))
        #print([f"{key}: {[str(y) for y in value]}" for key, value in potential_mappings.items()])
        return potential_mappings
        
                
        

if __name__ == "__main__":
    root = get_legal_ml_root("rioKB_GDPR.xml")
    rule_1 = get_rules_for_statement("statements83", root)
    rule_2 = get_rules_for_statement("statements84", root)#("statements34", root)
    print(rule_1[0].if_atoms)
    print(rule_2[1].if_atoms)
    pat = Pattern(rule_1[0].if_atoms, [Var(":t1")])
    print(pat.rule_contains_pattern(rule_2[0]))
    
    print(get_rules_for_statement("statements10", root)[0])
    parsed_expression = text_to_pattern("rioOnto:RexistAtTime(a1, t1) AND rioOnto:and'(a1, ep, er, edp) AND prOnto:DataSubject(w) AND prOnto:PersonalData(z, w) AND prOnto:Controller(y, fun(dapreco:vitalInterest(a, b))) AND prOnto:Processor(x)", [])
    print([str(x) for x in parsed_expression])