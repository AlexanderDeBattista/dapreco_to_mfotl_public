from atomic_concepts.interfaces import TimeRelation, AtomContent

class Eventuality(TimeRelation):
    def __init__(self, start: AtomContent, end: AtomContent, content: [AtomContent]) -> None:
        super().__init__(start, end, content)

    def __str__(self) -> str:
        return f"Eventually{super().__str__()}"