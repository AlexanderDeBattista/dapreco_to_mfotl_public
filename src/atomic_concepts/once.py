from atomic_concepts.interfaces import TimeRelation, AtomContent

class Once(TimeRelation):
    def __init__(self, start: AtomContent, end: AtomContent, content: [AtomContent]) -> None:
        super().__init__(start, end, content)
    
    def __str__(self) -> str:
        return f"Once{super().__str__()}"