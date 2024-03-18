from atomic_concepts.interfaces import AtomContent

class After(AtomContent):
    def __init__(self, first: AtomContent, second: AtomContent) -> None:
        self.t1 = first
        self.t2 = second
        super().__init__()
    
    def __str__(self) -> str:
        return f"after({self.t1}, {self.t2})"
    
    def __contains__(self, key):
        return key in self.t1 or key in self.t2