import bisect

class Utils:
    def __init__(self):
        pass

    def ForLoopSearch(self, container, value):
        for item in container:
            if item == value:
                return True
        return False

    def BisectSearch(self, container, value):
        return (
        (index := bisect.bisect_left(container, value)) < len(container) 
        and container[index] == value
        )