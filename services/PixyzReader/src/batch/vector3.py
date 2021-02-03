
class Vector3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def Get(self):
        return {
            "x": float(format(self.x, 'f')),
            "y": float(format(self.y, 'f')),
            "z": float(format(self.z, 'f'))
        }