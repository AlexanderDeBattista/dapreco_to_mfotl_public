from atomic_concepts.interfaces import AtomIterable
from atomic_concepts.relation import Relation
from atomic_concepts.before import Before
from atomic_concepts.after import After
from atomic_concepts.var import Var
from atomic_concepts.expression import Expression
from atomic_concepts.ind import Ind



class Atom(AtomIterable):
    
    def __init__(self, reified) -> None:
        self.atom_content = []
        self.reified = reified
        self.naf = False
    
    def is_naf(self):
        return self.naf

    def set_naf(self,naf_bool : bool):
        self.naf = naf_bool
    
    def add_rel(self, rel: Relation):
        assert isinstance(rel, Relation)
        self.atom_content.append(rel)
    
    def add_before(self, before: Before):
        assert isinstance(before, Before)
        self.atom_content.append(before)
    
    def add_after(self, after: After):
        assert isinstance(after, After)
        self.atom_content.append(after)
    
    def add_var(self, var: Var):
        assert isinstance(var, Var)
        self.atom_content.append(var)
        
    def add_expression(self, expr: Expression):
        assert isinstance(expr, Expression)
        self.atom_content.append(expr)
    
    def add_ind(self, ind: Ind):
        assert isinstance(ind, Ind)
        self.atom_content.append(ind)
    
    def get_predicates(self):
        predicates = []
        for item in self.atom_content:
            if isinstance(item, Relation):
                predicates.append((str(item.rel), [str(x) for x in item.content]))
        
        return predicates

    def get_atom_content(self):
        return self.atom_content

    def is_reified(self):
        return self.reified
    
    def un_reify(self):
        self.reified = False
        
    
    def __str__(self) -> str:
        base = ""
        if self.reified:
            # Adds a reified "tick" if the atom is reified
            base = f"'{self.atom_content[0]}{', '.join(self.atom_content[1:])}"
        else: base = ", ".join(str(x) for x in self.atom_content)
        
        if self.is_naf():
            return f"NAF({base})"
        return base
    
    def __contains__(self, key):
        for cont in self.get_atom_content():
            if key in cont:
                return True
        return False

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Atom):
            return False
        
        if not self.reified == __value.reified:
            return False
        
        if not len(self.atom_content) == len(__value.atom_content):
            return False

        for i in range(len(self.atom_content)):
            if not self.atom_content[i] == __value.atom_content[i]:
                return False
        
        return True
    
    def __iter__(self):
        return iter(self.atom_content)
