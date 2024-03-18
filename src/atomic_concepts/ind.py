from atomic_concepts.interfaces import AtomContent
from atomic_concepts.simple_value import SimpleValue

class Ind(AtomContent):
    def __init__(self, ind_val) -> None:
        super().__init__()
        self.ind_val = SimpleValue(ind_val)
    
    def __str__(self) -> str:
        return str(self.ind_val)
    
    def __contains__(self, key):
        if not isinstance(key, Ind):
            return False
        return self.ind_val == key.ind_val