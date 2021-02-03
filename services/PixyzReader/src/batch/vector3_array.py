class Vector3Array:
    def __init__(self, array = [], divider = 1):
        self.vector3_array = []
        for item in array:
            VectorData = {}
            VectorData["x"] = float(item.x / divider)
            VectorData["y"] = float(item.y / divider)
            VectorData["z"] = float(item.z / divider)
            self.vector3_array.append(VectorData)

    def Get(self):
        return self.vector3_array