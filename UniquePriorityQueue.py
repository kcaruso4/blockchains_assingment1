import heapq

class UniquePriorityQueue():
    def __init__(self):
        self.heap = []
        self.set = set()

    def add(self, element, priority):
        if not element in self.set:
            heapq.heappush(self.heap, (priority, element))
            self.set.add(element)

    def get(self):
        priority, element = heapq.heappop(self.heap)
        self.set.remove(element)
        return element

    def empty(self):
        return len(self.set) == 0

    def length(self):
        return len(self.set)