from atomic_concepts import Atom
from atomic_concepts.interfaces import AtomContent

class LogicalConnective():
    def __init__(self, name: str, content: [AtomContent]):
        self.name = name
        self.content = content
    
    def get_content(self) -> [AtomContent]:
        return self.content

    def __iter__(self):
        return iter(self.content)
    
    def __str__(self) -> str:
        return f"({(' '+self.name+' ').join([str(x) for x in self.content])})"
    
class And(LogicalConnective):
    def __init__(self, content: [AtomContent]):
        super().__init__("AND", content)
    
    def __str__(self) -> str:
        return super().__str__()
    
class Not(LogicalConnective):
    def __init__(self, content: [AtomContent]):
        super().__init__("NOT", content)
    
    def __str__(self) -> str:
        return super().__str__()

class Or(LogicalConnective):
    def __init__(self, content: [Atom]):
        super().__init__("OR", content)
    
    def __str__(self) -> str:
        return super().__str__()

class Implies(LogicalConnective):
    def __init__(self, content: [Atom]):
        assert len(content) == 2 
        super().__init__("IMPLIES", content)
    
    def __str__(self) -> str:
        return f"({super().get_content()[0]}) IMPLIES ({super().get_content()[1]})"