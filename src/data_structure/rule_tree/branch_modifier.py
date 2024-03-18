from atomic_concepts import Var

class BranchModifier(Var):
    def __init__(self, name: str):
        super().__init__(":"+name)
    
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, BranchModifier): return False
        return super().__eq__(__value)
    
class And(BranchModifier):
    def __init__(self):
        super().__init__("AND")
    
    def __str__(self) -> str:
        return super().__str__()
    
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, And): return False
        return super().__eq__(__value)
class Not(BranchModifier):
    def __init__(self):
        super().__init__("NOT")
    
    def __str__(self) -> str:
        return super().__str__()
    
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Not): return False
        return super().__eq__(__value)

class Or(BranchModifier):
    def __init__(self):
        super().__init__("OR")
    
    def __str__(self) -> str:
        return super().__str__()
    
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Or): return False
        return super().__eq__(__value)

class Implies(BranchModifier):
    def __init__(self):
        super().__init__("IMPLIES")
    
    def __str__(self) -> str:
        return super().__str__()
    
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Implies): return False
        return super().__eq__(__value)

class TimeModifier(BranchModifier):
    def __init__(self, name: str, start: str, stop: str):
        super().__init__(name)
        self.start = start
        self.stop = stop
    
    def get_start(self):
        return self.start
    def get_end(self):
        return self.stop
    def get_content(self):
        return super()
    
    def set_start(self, start: str):
        self.start = start
    def set_end(self, end: str):
        self.stop = end
        
    def __str__(self) -> str:
        if self.start is None and self.stop is None:
            return super().__str__()
        return f"{super().__str__()} [{self.start}, {self.stop}]"
    
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, TimeModifier): return False
        return super().__eq__(__value) and self.start == __value.start and self.stop == __value.stop

class Once(TimeModifier):
    def __init__(self, start: str, stop: str):
        super().__init__("ONCE", start, stop)
    def get_start(self):
        return super().get_start()
    def get_end(self):
        return super().get_end()
    def get_content(self):
        return super().get_content()
    
    def set_start(self, start: str):
        super().set_start(start)
    def set_end(self, end: str):
        super().set_end(end)
        
    def __str__(self) -> str:
        return super().__str__()
    
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Once): return False
        return super().__eq__(__value)
    
class Eventually(TimeModifier):
    def __init__(self, start: str, stop: str):
        super().__init__("EVENTUALLY", start, stop)
    def get_start(self):
        return super().get_start()
    def get_end(self):
        return super().get_end()
    def get_content(self):
        return super().get_content()
    def __str__(self) -> str:
        return super().__str__()

    def set_start(self, start: str):
        super().set_start(start)
    def set_end(self, end: str):
        super().set_end(end)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Eventually): return False
        return super().__eq__(__value)

class Historically(TimeModifier):
    def __init__(self, start: str, stop: str):
        super().__init__("HISTORICALLY", start, stop)
    def get_start(self):
        return super().get_start()
    def get_end(self):
        return super().get_end()
    def get_content(self):
        return super().get_content()
    def __str__(self) -> str:
        return super().__str__()
    
    def set_start(self, start: str):
        super().set_start(start)
    def set_end(self, end: str):
        super().set_end(end)
    
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Historically): return False
        return super().__eq__(__value)

class Always(TimeModifier):
    def __init__(self, start: str, stop: str):
        super().__init__("ALWAYS", start, stop)
    
    def get_start(self):
        return super().get_start()
    def get_end(self):
        return super().get_end()
    def get_content(self):
        return super().get_content()
    def __str__(self) -> str:
        return super().__str__()
    
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Historically): return False
        return super().__eq__(__value)