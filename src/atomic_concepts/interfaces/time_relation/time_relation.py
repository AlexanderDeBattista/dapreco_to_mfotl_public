from atomic_concepts.interfaces import AtomContent, AtomIterable

class TimeRelation(AtomIterable):
    def __init__(self, start: AtomContent, end: AtomContent, content: [AtomContent]) -> None:
        self.start = start
        self.end = end
        self.content = content
        
    def __str__(self) -> str:
        return f"[{self.start}, {self.end}]( {'AND '.join(str(x) for x in self.content)})"
    
    def __contains__(self, key):
        for content in self.content:
            if key in content:
                return True
        return False
    
    def __iter__(self):
        return iter(self.content)