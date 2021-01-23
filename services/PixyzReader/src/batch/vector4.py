class Vector4:
    def __init__(self, x, y, z, w):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def Get(self):
        return {'x': format(self.x, 'f'), 'y': format(self.y, 'f'), 'z': format(self.z, 'f'), 'w': format(self.w, 'f')}