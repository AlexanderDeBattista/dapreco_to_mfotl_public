from atomic_concepts.interfaces import AtomContent

class Before(AtomContent):
    def __init__(self, t1: AtomContent, t2: AtomContent) -> None:
        self.t1 = t1
        self.t2 = t2
        super().__init__()

    def __str__(self) -> str:
        return f"before({str(self.t1)}, {str(self.t2)})"
    
    def __contains__(self, key):
        return key in self.t1 or key in self.t2