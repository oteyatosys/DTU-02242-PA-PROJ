class Bot:
    def __le__(self, _) -> bool:
        return True

    # Meet operation
    def __and__(self, other):
        return self

    # Join operation
    def __or__(self, other):
        return other

    def __hash__(self) -> int:
        return hash("⊥")

    def __eq__(self, other):
        return isinstance(other, Bot)

    def __repr__(self) -> str:
        return "⊥"
    
    def widening(self, K, other):
        return other
