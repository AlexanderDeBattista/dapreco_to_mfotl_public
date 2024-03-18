from atomic_concepts.interfaces import AtomContent

class AtomIterable(AtomContent):
    def __init__(self) -> None:
        pass
    
    def __iter__(self):
        raise Exception("This method should be implemented in the subclass")
 