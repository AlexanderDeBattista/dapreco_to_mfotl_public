from atomic_concepts.interfaces import AtomIterable, AtomContent

class Relation(AtomIterable):
    def __init__(self,rel: str) -> None:
        super().__init__()
        self.rel = rel
        self.content = []
    
    def add_relation_content(self, data: AtomContent):
        assert isinstance(data, AtomContent)
        self.content.append(data)
        
    def get_rel_name(self):
        return self.rel
    
    def update_content(self, new_content: []):
        self.content = new_content
    
    def get_rel_content(self):
        return self.content
        
    def __str__(self) -> str:
        return self.rel + "(" + ", ".join(str(x) for x in self.content) +")"

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Relation):
            return False
        
        if not self.rel == __value.rel:
            return False
        
        if not len(self.content) == len(__value.content):
            return False
        
        for i in range(len(self.content)):
            if not self.content[i] == __value.content[i]:
                return False
        
        return True
    
    def __contains__(self, key):
        for content in self.content:
            if key in content:
                return True
        return False
    
    def __iter__(self):
        return iter(self.content)