from atomic_concepts import Atom, Var
from rule.logical_connectives import And, Implies, Not, Or, LogicalConnective

class Rule():
    
    def __init__(self, if_exist: [Var], then_exist: [Var], if_atoms: [Atom], then_atoms: [Atom]) -> None:
        self.if_exist = if_exist
        self.then_exist = then_exist
        
        self.if_atoms = if_atoms
        self.then_atoms = then_atoms
        
        
        #self.add_and_connectives()
    
    def __str__(self) -> str:
        if_conjugations = " AND ".join(str(x) for x in self.if_atoms)
        then_conjugation = " AND ".join(str(x) for x in self.then_atoms)
        if_str = f"""{'' if len(self.if_exist) == 0 else 'EXISTS '} {' . '.join([str(x) for x in self.if_exist])} {'' if len(self.if_exist) == 0 else '. '}({if_conjugations})"""
        then_str = f"""IMPLIES {'' if len(self.then_exist) == 0 else 'EXISTS '} {' . '.join([str(x) for x in self.then_exist])} {'' if len(self.then_exist) == 0 else '. '}({then_conjugation})"""
        
        return if_str + "\n" +then_str
        
    def get_predicates_as_monpoly_sig(self) -> str:
        """ Constructs a signature string for MonPoly, that defines which predicates are used in a given rule

        Returns:
            str: MonPoly compatible signature string for the given rule
        """
        predicates = []
        for atom in self.if_atoms:
            if isinstance(atom, Atom):
                for val in atom.get_predicates():
                    predicates.append(val)
        for atom in self.then_atoms:
            for val in atom.get_predicates():
                    predicates.append(val)
        
        sig = ""
        for predicate_name, arguments in predicates:
            sig += f"{predicate_name}({':int,'.join(arguments)}:int)\n"
            
        return sig
