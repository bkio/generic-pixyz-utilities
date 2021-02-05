from .pixyz_algorithms import PixyzAlgorithms
from .logger import Logger
from .vector3_array import Vector3Array
from .PB.protob_messages_pb2 import PLOD

import pxz
try:# Prevent IDE errors
    from pxz import polygonal
except: pass

class GeometryMesh:
    def __init__(self, proto: PLOD, occurrence, lod_mesh, small_object_threshold = 50, scale_factor = 1000):
        #Parameters
        self.proto = proto
        self.occurrence = occurrence
        self.lod_mesh = lod_mesh
        self.small_object_threshold = small_object_threshold
        self.scale_factor = scale_factor

        #Returns
        self.has_lod = True
        self.error_message = None

        meshDefinition = polygonal.getMeshDefinition(self.lod_mesh)

        meshVertices = meshDefinition.vertices
        meshNormals = meshDefinition.normals
        meshTangents = meshDefinition.normals
        meshTriangles = meshDefinition.triangles

        vertices_len = len(meshVertices)
        normals_len = len(meshNormals)
        tangents_len = len(meshTangents)
        triangles_len = len(meshTriangles)

        if vertices_len != normals_len or normals_len != tangents_len:
            self.error_message = f"Vertices, normals, and tangents must be same. Please check your model. Vertices Count={vertices_len}, Normals Count={normals_len}, Tangents Count={tangents_len}"

        if vertices_len > 0 and triangles_len == 0:
            self.error_message = f"If your triangles count is equal to 0 (zero), vertices count must be 0 (zero). Please check your model. Vertices Count={vertices_len}, Triangles Count={triangles_len}"

        if triangles_len > 0 and triangles_len % 3 != 0:
            self.error_message = f"Triangles count must be divided by 3. Please check your model. Triangles Count={triangles_len}"

        vertices = Vector3Array(meshVertices, self.scale_factor).Get()
        normals = Vector3Array(meshNormals).Get()
        tangents = Vector3Array(meshTangents).Get()
        indexes = meshTriangles

        if self.__IsSmallObject(vertices) == True:
            PixyzAlgorithms().DeleteOccurrences([occurrence])
            self.has_lod = False
            pass
        else:
            self.proto.Indexes.extend(indexes)
            for i in range(vertices_len):
                vnt = self.proto.VertexNormalTangentList.add()
                vnt.Vertex.X = vertices[i]["x"]
                vnt.Vertex.Y = vertices[i]["y"]
                vnt.Vertex.Z = vertices[i]["z"]

                vnt.Normal.X = normals[i]["x"]
                vnt.Normal.Y = normals[i]["y"]
                vnt.Normal.Z = normals[i]["z"]
                
                vnt.Tangent.X = tangents[i]["x"]
                vnt.Tangent.Y = tangents[i]["y"]
                vnt.Tangent.Z = tangents[i]["z"]

    def __IsSmallObject(self, vertices):
        if self.small_object_threshold <= 0:
            return False
            
        bbmax = {}
        bbmax['x'] = -999999
        bbmax['y'] = -999999
        bbmax['z'] = -999999

        bbmin = {}
        bbmin['x'] = 999999
        bbmin['y'] = 999999
        bbmin['z'] = 999999

        i = 0
        while i < len(vertices):
            if bbmax['x'] < vertices[i]['x']:
                bbmax['x'] = vertices[i]['x']
            if bbmax['y'] < vertices[i]['y']:
                bbmax['y'] = vertices[i]['y']
            if bbmax['z'] < vertices[i]['z']:
                bbmax['z'] = vertices[i]['z']
            if bbmin['x'] > vertices[i]['x']:
                bbmin['x'] = vertices[i]['x']
            if bbmin['y'] > vertices[i]['y']:
                bbmin['y'] = vertices[i]['y']
            if bbmin['z'] > vertices[i]['z']:
                bbmin['z'] = vertices[i]['z']
            i += 1

        x = (bbmax['x'] - bbmin['x']) * self.scale_factor
        y = (bbmax['y'] - bbmin['y']) * self.scale_factor
        z = (bbmax['z'] - bbmin['z']) * self.scale_factor

        if x < self.small_object_threshold and y < self.small_object_threshold and z < self.small_object_threshold:
            return True
        
        return False

    def Get(self):
        return [self.has_lod, self.error_message]