class Vector3Array:
    def __init__(self, array = [], divider = 1):
        self.vector3_array = []
        for item in array:
            VectorData = {}
            VectorData["x"] = item.x / divider
            VectorData["y"] = item.y / divider
            VectorData["z"] = item.z / divider
            self.vector3_array.append(VectorData)

    def Get(self):
        return self.vector3_array