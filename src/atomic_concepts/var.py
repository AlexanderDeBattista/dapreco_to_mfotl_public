from atomic_concepts.interfaces import AtomContent
from atomic_concepts.simple_value import SimpleValue

class Var(AtomContent):
    def __init__(self, var_val: str, defined_now = False) -> None:
        super().__init__()
        self.var_val = SimpleValue(var_val)
        self.defined_now = defined_now
    
    def get_var_val(self):
        return self.var_val
    
    def __str__(self) -> str:
        val_str = str(self.var_val)
        assert val_str[0] == ":"
        return val_str[1:]

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Var):
            return False
        # TODO: Compare based on var_val AND defined_now?
        return self.var_val == __value.get_var_val()

    def __contains__(self, key):
        return self.__eq__(key)
    
    def __hash__(self) -> int:
        # TODO: Hash based on defined now bool as well?
        return (hash(self.var_val)) % 2**32