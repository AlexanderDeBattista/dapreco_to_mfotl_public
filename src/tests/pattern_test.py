from pattern.pattern import Pattern
from atomic_concepts import Relation, Var, Atom
from atomic_concepts.interfaces import AtomIterable, AtomContent
from name_space import NameSpace
from util.legal_ml_parser import get_legal_ml_root, get_rules_for_statement

import copy
import unittest
import uuid

class TestPattern(unittest.TestCase):
    
    def __init__(self, methodName: str = "runTest") -> None:
        self.gdpr_root = get_legal_ml_root("rioKB_GDPR.xml")
        super().__init__(methodName)
        
    def test_pattern_found_t1(self):
        t1_atom = Atom(False)
        t1_relation = Relation(NameSpace.RIOONTO.value + ":RexistAtTime")
        t1_relation.add_relation_content(Var(":a1"))
        t1_relation.add_relation_content(Var(":t1"))
        t1_atom.add_rel(t1_relation)
        
        t1_pattern = Pattern([t1_atom], [])
        
        rule_1 = get_rules_for_statement("statements1", self.gdpr_root)
        
        
        self.assertEqual(t1_pattern.rule_contains_pattern(rule_1[0]), True)
        
    def test_pattern_found_itself(self):
        rule = get_rules_for_statement("statements1", self.gdpr_root)
        pattern = Pattern(rule[0].if_atoms, [])
        
        self.assertEqual(pattern.rule_contains_pattern(rule[0]), True)
        
    def test_pattern_found_itself_with_restricted_names(self):
        rule = get_rules_for_statement("statements1", self.gdpr_root)
        var_list = self.get_vars_contained_in(rule[0].if_atoms)
        
        pattern = Pattern(rule[0].if_atoms, var_list)
        
        self.assertEqual(pattern.rule_contains_pattern(rule[0]), True)
        
    def test_pattern_found_with_diff_names(self):
        
        t1_atom = Atom(False)
        t1_relation = Relation(NameSpace.RIOONTO.value + ":RexistAtTime")
        t1_relation.add_relation_content(Var(":"+str(uuid.uuid4())))
        t1_relation.add_relation_content(Var(":"+str(uuid.uuid4())))
        t1_atom.add_rel(t1_relation)
        
        rule = get_rules_for_statement("statements1", self.gdpr_root)
        
        pattern = Pattern([t1_atom], [])
        
        self.assertEqual(pattern.rule_contains_pattern(rule[0]), True)
    
    def test_pattern_not_found_with_restricted_names(self):
        t1_atom = Atom(False)
        t1_relation = Relation(NameSpace.RIOONTO.value + ":RexistAtTime")
        var_1 = Var(str(uuid.uuid4()))
        var_2 = Var(str(uuid.uuid4()))
        t1_relation.add_relation_content(var_1)
        t1_relation.add_relation_content(var_2)
        t1_atom.add_rel(t1_relation)
        
        rule = get_rules_for_statement("statements1", self.gdpr_root)
        
        pattern = Pattern([t1_atom], [var_1])
        
        self.assertEqual(pattern.rule_contains_pattern(rule[0]), False)
    
    def test_pattern_not_statement2_in_statement1(self):
        rule_1 = get_rules_for_statement("statements1", self.gdpr_root)
        rule_2 = get_rules_for_statement("statements2", self.gdpr_root)
        
        pattern = Pattern(rule_2[0].if_atoms, [])
        
        self.assertEqual(pattern.rule_contains_pattern(rule_1[0]), False)
        
    def test_pattern_statement1_in_statement2(self):
        rule_1 = get_rules_for_statement("statements1", self.gdpr_root)
        rule_2 = get_rules_for_statement("statements2", self.gdpr_root)
        
        pattern = Pattern(rule_1[0].if_atoms, [])
        
        self.assertEqual(pattern.rule_contains_pattern(rule_2[0]), True)
        
        
    def get_vars_contained_in(self, items: [AtomContent]) -> [Var]:
        var_list = []
        rule_queue = [copy.deepcopy(items)]
        while len(rule_queue) > 0:
            curr = rule_queue.pop()
            if isinstance(curr, Var):
                var_list.append(curr)
            elif isinstance(curr, AtomIterable):
                for item in curr:
                    rule_queue.append(item)
        return var_list
        
if __name__ == "__main__":
    unittest.main()