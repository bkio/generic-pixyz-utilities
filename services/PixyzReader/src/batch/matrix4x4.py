import math
from .vector3 import Vector3

class Matrix4x4:
    def __init__(self, matrix, part_matrix = None, scale_factor = 1000):
        self.matrix = matrix
        self.part_matrix = part_matrix
        self.scale_factor = scale_factor

    def GetTranslation(self):
        # convert from mm to cm
        x = self.matrix[0][3] / self.scale_factor
        y = self.matrix[1][3] / self.scale_factor
        z = self.matrix[2][3] / self.scale_factor
        return Vector3(x,y,z)

    def GetEulerRotation(self):
        sy = math.sqrt(self.matrix[0][0] * self.matrix[0][0] +  self.matrix[1][0] * self.matrix[1][0])

        singular = sy < 1e-6

        if not singular:
            x = math.atan2(self.matrix[2][1] , self.matrix[2][2])
            y = math.atan2(self.matrix[2][0], sy)
            z = math.atan2(self.matrix[1][0], self.matrix[0][0])
        else:
            x = math.atan2(-self.matrix[1][2], self.matrix[1][1])
            y = math.atan2(-self.matrix[2][0], sy)
            z = 0

        return Vector3(math.degrees(x),math.degrees(y),math.degrees(z))

    def __GetScaleXYZ(self, mat):
        xs = -1 if mat[0][0] * mat[0][1] * mat[0][2] < 0 else 1
        ys = -1 if mat[1][0] * mat[1][1] * mat[1][2] < 0 else 1
        zs = -1 if mat[2][0] * mat[2][1] * mat[2][2] < 0 else 1
        
        x = xs * math.sqrt(mat[0][0] * mat[0][0] + mat[0][1] * mat[0][1] + mat[0][2] * mat[0][2])
        y = ys * math.sqrt(mat[1][0] * mat[1][0] + mat[1][1] * mat[1][1] + mat[1][2] * mat[1][2])
        z = zs * math.sqrt(mat[2][0] * mat[2][0] + mat[2][1] * mat[2][1] + mat[2][2] * mat[2][2])
        
        return [x, y, z]

    def GetScale(self):
        x1, y1, z1 = self.__GetScaleXYZ(self.matrix)
        if self.part_matrix != None:
            x2, y2, z2 = self.__GetScaleXYZ(self.part_matrix)
        else:
            x2, y2, z2 = [1, 1, 1]
        
        x = x1 * x2
        y = y1 * y2
        z = z1 * z2

        return Vector3(x,y,z)