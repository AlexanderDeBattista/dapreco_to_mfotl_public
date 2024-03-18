from atomic_concepts.interfaces import AtomContent
from .function import Function

class Expression(AtomContent):
    def __init__(self, function: Function) -> None:
        super().__init__()
        self.fun = function
    
    def __str__(self) -> str:
        return str(self.fun)
    
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Expression):
            return False
        return self.fun == __value.fun

    def __contains__(self, key):
        return key in self.fun
    
    def __hash__(self) -> int:
        return hash(self.fun)
