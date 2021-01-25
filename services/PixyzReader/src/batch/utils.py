import bisect

class Utils:
    def __init__(self):
        self.init_value = True
    
    def BisectSearch(container, value):
        return (
        (index := bisect.bisect_left(container, value)) < len(container) 
        and container[index] == value
        )