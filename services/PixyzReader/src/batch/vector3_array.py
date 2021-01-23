class Vector3Array:
    def __init__(self, array = [], divider = 1):
        self.vector3_array = []
        for item in array:
            vector = {}
            vector['x'] = item.x / divider
            vector['y'] = item.y / divider
            vector['z'] = item.z / divider
            self.vector3_array.append(vector)

    def Get(self):
        return self.vector3_array