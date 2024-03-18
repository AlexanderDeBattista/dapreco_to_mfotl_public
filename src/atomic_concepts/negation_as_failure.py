from atomic_concepts.interfaces import AtomContent
from .atom import Atom

class NegationAsFailure(AtomContent):
    def __init__(self, atom: Atom) -> None:
        super().__init__()
        self.atom = atom
    
    def __str__(self) -> str:
        return f"naf({str(self.atom)})"
    
    def __contains__(self, key):
        return key in self.atom