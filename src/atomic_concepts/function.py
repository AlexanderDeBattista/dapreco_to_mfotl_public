from atomic_concepts.interfaces import AtomIterable, AtomContent

class Function(AtomIterable):
    
    def __init__(self, fun_name: str, arguments: [AtomContent]) -> None:
        self.fun_name = fun_name
        self.arguments = arguments
        super().__init__()
    
    def __str__(self) -> str:
        return f"fun({self.fun_name}({', '.join(str(x) for x in self.arguments)}))"

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Function):
            return False
        
        if not self.fun_name == __value.fun_name:
            return False
        
        if not len(self.arguments) == len(__value.arguments):
            return False
        
        for i in range(len(self.arguments)):
            if not self.arguments[i] == __value.arguments[i]:
                return False
        
        return True
        
    def __contains__(self, key):
        for arg in self.arguments:
            if key in arg:
                return True
        
        return False
    
    def __iter__(self):
        return iter(self.arguments)
    
    def __hash__(self) -> int:
        i = 1
        argument_hash = [sum(hash(arg)**i for i, arg in enumerate(self.arguments))][0]
        return (hash(self.fun_name)+argument_hash)%2**32