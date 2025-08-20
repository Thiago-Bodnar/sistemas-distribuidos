from functools import total_ordering

@total_ordering
class Request:
    def __init__(self, id, time):
        self.id = id
        self.time = time

    def __lt__(self, other):
        return self.time < other.time
