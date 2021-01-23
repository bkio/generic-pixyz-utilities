class Vector3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def Get(self):
        return {'x': format(self.x, 'f'), 'y': format(self.y, 'f'), 'z': format(self.z, 'f')}