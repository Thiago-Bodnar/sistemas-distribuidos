from functools import total_ordering

@total_ordering

class Request:
    def _init_(self, id, time):
        self.id = id
        self.time = time

    def _lt_(self, other):
        return self.time < other.time
