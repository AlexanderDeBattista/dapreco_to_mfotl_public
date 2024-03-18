from atomic_concepts.interfaces import AtomContent
from rule.rule import Rule
from rule.logical_connectives import And, Implies, Not, Or, LogicalConnective
from util.legal_ml_parser.legal_ml_parser import get_legal_ml_root, get_rules_for_statement

class MfotlRule():
    def __init__(self, rule: LogicalConnective) -> None:
        self.rule = rule
        
    def __str__(self) -> str:
        return str(self.rule)
        
def rule_to_mfotl_rule(rule: Rule) -> MfotlRule:
    left_connective = And(rule.if_atoms)
    right_connective = And(rule.then_atoms)
    
    implication = Implies([left_connective, right_connective])
    
    return MfotlRule(implication)


if __name__ == "__main__":
    root = get_legal_ml_root("rioKB_GDPR.xml")
    rules = get_rules_for_statement("statements1", root)
    
    print(rule_to_mfotl_rule(rules[0]))