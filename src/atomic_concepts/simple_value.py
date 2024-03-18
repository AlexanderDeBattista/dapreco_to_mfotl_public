from atomic_concepts.interfaces import AtomContent

class SimpleValue(AtomContent):
    def __init__(self, val: str) -> None:
        self.val = val
        super().__init__()
  
    def get_val(self):
        return self.val
      
    def __str__(self) -> str:
        return self.val
    
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, SimpleValue):
            return False
        return self.val == __value.get_val()
    
    def __contains__(self, key):
        return self.__eq__(key)
    
    def __hash__(self) -> int:
        return hash(self.val)