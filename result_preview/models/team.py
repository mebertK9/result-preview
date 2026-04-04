
class Team:
    def __init__(self, name):
        self.name = name
        self.calculate = True

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, Team) and self.name == other.name

    def __hash__(self):
        return hash(self.name)
