from .logger import Logger
import enum

import pxz
try:# Prevent IDE errors
    from pxz import algo
    from pxz import scene
    from pxz import core
    from pxz import generateproxy
    from pxz import material
    from pxz import polygonal
    from pxz import scenario
except: pass

class UVGenerationMode(enum.Enum):
    NoUV = 0
    FastUV = 1
    UniformUV = 2

class PixyzAlgorithms():
    """ 
    The wrapper class for describing Pixyz Algorithms for better documentation
    """
    def __init__(self, verbose = False):
        self.root = scene.getRoot()
        self.verbose = verbose

    def RepairCAD(self, occurrences = [], tolerance = 0.1, orient = False):
        """ 
        Repair CAD shapes, assemble faces, remove duplicated faces, optimize loops and repair topology
    
        - Parameters:\n
            - occurrences (OccurrenceList) : Occurrences of components to clean, default is scene.getRoot()\n
            - tolerance (Distance) : Tolerance in mm, default is 0.1 mm\n
            - orient (Boolean) [optional] : If true reorient the model, default is False\n
    
        - Returns:\n
            - void\n
        """
        if self.verbose:
            Logger('before repairCAD').PrintModelInfo(self.root)
        
        if len(occurrences) == 0:
            occurrences = [self.root]
        
        algo.repairCAD(occurrences, tolerance, orient)

    def Tesellate(self, occurrences = [], maxSag = 2.0, maxLength = -1, maxAngle = -1, createNormals = True, uvMode = UVGenerationMode.NoUV.value, uvChannel = 1, uvPadding = 0.0, createTangents = True, createFreeEdges = False, keepBRepShape = False, overrideExistingTessellation = False):
        """
        Create a tessellated representation from a CAD representation for each given part

        - Parameters: \n
            - occurrences (OccurrenceList) : Occurrences of components to tessellate\n
            - maxSag (Distance) : Maximum distance between the geometry and the tessellation\n
            - maxLength (Distance) : Maximum length of elements\n
            - maxAngle (Angle) : Maximum angle between normals of two adjacent elements\n
            - createNormals (Boolean) [optional] : If true, normals will be generated\n
            - uvMode (UVGenerationMode) [optional] : Select the texture coordinates generation mode\n
            - uvChannel (Int) [optional] : The UV channel of the generated texture coordinates (if any)\n
            - uvPadding (Double) [optional] : The UV padding between UV island in UV coordinate space (between 0-1). This   parameter is handled as an heuristic so it might not be respected\n
            - createTangents (Boolean) [optional] : If true, tangents will be generated\n
            - createFreeEdges (Boolean) [optional] : If true, free edges will be created for each patch borders\n
            - keepBRepShape (Boolean) [optional] : If true, BRep shapes will be kept for Back to Brep or Retessellate\n
            - overrideExistingTessellation (Boolean) [optional] : If true, already tessellated parts will be re-tessellated\n

        - Returns:\n
            - void\n

        """
        if self.verbose:
            Logger('before tessellate').PrintModelInfo(self.root)

        if len(occurrences) == 0:
            occurrences = [self.root]

        algo.tessellate(occurrences, maxSag, maxLength, maxAngle, createNormals, uvMode, uvChannel, uvPadding, createTangents, createFreeEdges, keepBRepShape, overrideExistingTessellation)

    def RepairMesh(self, occurrences = [], tolerance = 0.1, crackNonManifold = True, orient = False):
        """
        Launch the repair process to repair a disconnected or not clean tessellation

        - Parameters: \n
            - occurrences (OccurrenceList) : Occurrences of components to process\n
            - tolerance (Distance) : Connection tolerance in mm\n
            - crackNonManifold (Bool) [optional] : At the end of the repair process, crack resulting non-manifold edges\n
            - orient (Boolean) [optional] : If true reorient the model\n

        - Returns:\n
            - void\n

        """
        if self.verbose:
            Logger('before repairMesh').PrintModelInfo(self.root)

        if len(occurrences) == 0:
            occurrences = [self.root]

        algo.repairMesh(occurrences, tolerance, crackNonManifold, orient)

    def ExplodePartByMaterials(self, occurrences = []):
        """
        Explode all parts by material

        - Parameters: \n
            - occurrences (OccurrenceList) : Occurrences of part to process\n

        - Returns:\n
            - void\n

        """
        if self.verbose:
            Logger('before explodePartByMaterials').PrintModelInfo(self.root)

        if len(occurrences) == 0:
            occurrences = [self.root]

        algo.explodePartByMaterials(occurrences)

    def DeletePatches(self, occurrences = [], keepOnePatchByMaterial = True):
        """
        Delete patches attributes on tessellations

        - Parameters: \n
            - occurrences (OccurrenceList) : Occurrences of components to process\n
            - keepOnePatchByMaterial (Boolean) [optional] : If set, one patch by material will be kept, else all patches will be deleted and materials on patches will be lost\n

        - Returns:\n
            - void\n

        """
        if self.verbose:
            Logger('before deletePatches').PrintModelInfo(self.root)

        if len(occurrences) == 0:
            occurrences = [self.root]

        algo.deletePatches(occurrences, keepOnePatchByMaterial)

    def DeleteLines(self, occurrences = []):
        """
        Delete all free line of the mesh of given parts

        - Parameters: \n
            - occurrences (OccurrenceList) : Occurrences of components to process\n

        - Returns:\n
            - void\n

        """
        if self.verbose:
            Logger('before deleteLines').PrintModelInfo(self.root)

        if len(occurrences) == 0:
            occurrences = [self.root]

        algo.deleteLines(occurrences)

    def DeleteFreeVertices(self, occurrences = []):
        """
        Delete all free vertices of the mesh of given parts

        - Parameters: \n
            - occurrences (OccurrenceList) : Occurrences of components to process\n

        - Returns:\n
            - void\n

        """
        if self.verbose:
            Logger('before deleteFreeVertices').PrintModelInfo(self.root)

        if len(occurrences) == 0:
            occurrences = [self.root]

        algo.deleteFreeVertices(occurrences)

    def Triangularize(self, occurrences = []):
        """
        Split all non-triangle polygons in the meshes to triangles

        - Parameters: \n
            - occurrences (OccurrenceList) : Occurrences of components to process\n

        - Returns:\n
            - void\n

        """
        if self.verbose:
            Logger('before triangularize').PrintModelInfo(self.root)

        if len(occurrences) == 0:
            occurrences = [self.root]

        algo.triangularize(occurrences)

    def CreateNormals(self, occurrences = [], sharpEdge = -1.0, override = True, useAreaWeighting = False):
        """
        Create normal attributes on tessellations

        - Parameters: \n
            - occurrences (OccurrenceList) : Occurrences of components to create attributes\n
            - sharpEdge (Angle) [optional] : Edges with an angle between their polygons greater than sharpEdge will be considered sharp (default use the Pixyz sharpAngle parameter)\n
            - override (Boolean) [optional] : If true, override existing normals, else only create normals on meshes without normals\n
            - useAreaWeighting (Boolean) [optional] : If true, normal computation will be weighted using polygon areas\n

        - Returns:\n
            - void\n

        """
        if self.verbose:
            Logger('before createNormals').PrintModelInfo(self.root)

        if len(occurrences) == 0:
            occurrences = [self.root]

        algo.createNormals(occurrences, sharpEdge, override, useAreaWeighting)

    def MakeInstanceUnique(self, occurrences = []):
        """
        Singularize all instances on the sub-tree of an occurrence

        - Parameters: \n
            - occurrences (OccurrenceList) [optional] : Root occurrence for the process\n

        - Returns:\n
            - void\n

        """
        if self.verbose:
            Logger('before makeInstanceUnique').PrintModelInfo(self.root)

        if len(occurrences) == 0:
            occurrences = [self.root]

        scene.makeInstanceUnique(occurrences)

    def CreateInstancesBySimilarity(self, occurrences = [], dimensionsSimilarity = 1.0, polycountSimilarity = 1.0, ignoreSymmetry = True, keepExistingPrototypes = False, createNewOccurrencesForPrototypes = True):
        """
        Create instances when there are similar parts.\n
        This can be used to repair instances or to simplify a model that has similar parts that could be instanciated instead to reduce the number of unique meshes (reduces drawcalls, GPU memory usage and file size).\n
        Using 1.0 (100%) in all similarity criterias is non destructive.\n
        Using lower values will help finding more similar parts, even if their polycount or dimensions varies a bit.

        - Parameters: \n
                - occurrences (OccurrenceList) : Occurrence for which we want to find similar parts and create instances using prototypes.\n
                - dimensionsSimilarity (Coeff) : The percentage of similarity on dimensions. A value of 1.0 (100%) will find parts that have exactly the same dimensions. A lower value will increase the likelyhood to find similar parts, at the cost of precision.\n
                - polycountSimilarity (Coeff) : The percentage of similarity on polycount. A value of 1.0 (100%) will find parts that have exactly the same polycount. A lower value will increase the likelyhood to find similar parts, at the cost of precision.\n
                - ignoreSymmetry (Boolean) : If True, symmetries will be ignored, otherwise negative scaling will be applied in the occurrence transformation.\n
                - keepExistingPrototypes (Boolean) : If True, existing prototypes will be kept. Otherwise, the selection will be singularized and instanced will be created from scratch.\n
                - createNewOccurrencesForPrototypes (Boolean) : If True, a new occurrence will be created for each prototype. Those occurrences won't appear in the hierarchy, and so deleting one of the part in the scene has no risks of singularizing. If set to False, an arbitrary occurrence will be used as the prototype for other similar occurrences, which is less safe but will result in less occurrences.\n

        - Returns:\n
            - void\n

        """
        if self.verbose:
            Logger('before createInstancesBySimilarity').PrintModelInfo(self.root)

        if len(occurrences) == 0:
            occurrences = [self.root]

        scenario.createInstancesBySimilarity(occurrences, dimensionsSimilarity, polycountSimilarity, ignoreSymmetry, keepExistingPrototypes, createNewOccurrencesForPrototypes)

    def Decimate(self, occurrences = [], surfacicTolerance = 3.0, lineicTolerance = -1, normalTolerance = 15.0, texCoordTolerance = -1, releaseConstraintOnSmallArea = False):
        """
        Reduce the polygon count by removing some vertices\n
        Function defaults are addressed Strong preset settings which means low triangle counts\n

        - Parameters: \n
            - occurrences (OccurrenceList) : Occurrences of components to process\n
            - surfacicTolerance (Distance) : Maximum distance between surfacic vertices and resulting simplified surfaces\n
            - lineicTolerance (Distance) [optional] : Maximum distance between lineic vertices and resulting simplified lines\n
            - normalTolerance (Angle) [optional] : Maximum angle between original normals and those interpolated on the simplified surface\n
            - texCoordTolerance (Double) [optional] : Maximum distance (in UV space) between original texcoords and those interpolated on the simplified surface\n
            - releaseConstraintOnSmallArea (Boolean) [optional] : If True, release constraint of normal and/or texcoord tolerance on small areas (according to surfacicTolerance)\n

        - Returns:\n
            - void\n

        """
        if self.verbose:
            Logger('before decimate').PrintModelInfo(self.root)

        if len(occurrences) == 0:
            occurrences = [self.root]

        algo.decimate(occurrences, surfacicTolerance, lineicTolerance, normalTolerance, texCoordTolerance, releaseConstraintOnSmallArea)
    
    def DecimateMedium(self, occurrences = []):
        """
        Reduce the polygon count by removing some vertices with medium preset settings which means medium triangle counts\n
        surfacicTolerance = 1.0\n
        lineicTolerance = -1\n
        normalTolerance = 8.0\n
        texCoordTolerance = -1\n
        releaseConstraintOnSmallArea = False\n

        - Parameters: \n
            - occurrences (OccurrenceList) : Occurrences of components to process\n
        - Returns:\n
            - void\n

        """
        if self.verbose:
            Logger('before decimate').PrintModelInfo(self.root)

        if len(occurrences) == 0:
            occurrences = [self.root]

        self.Decimate(occurrences, 1.0, -1, 8.0, -1, False)

    def DecimateLow(self, occurrences = []):
        """
        Reduce the polygon count by removing some vertices with low preset settings which means high triangle counts\n
        surfacicTolerance = 0.5\n
        lineicTolerance = 0.1\n
        normalTolerance = 1.0\n
        texCoordTolerance = -1\n
        releaseConstraintOnSmallArea = False\n

        - Parameters: \n
            - occurrences (OccurrenceList) : Occurrences of components to process\n
        - Returns:\n
            - void\n

        """
        if self.verbose:
            Logger('before decimate').PrintModelInfo(self.root)

        if len(occurrences) == 0:
            occurrences = [self.root]

        self.Decimate(occurrences, 0.5, 0.1, 1.0, -1, False)

    def DecimateBest(self, occurrences = []):
        """
        Reduce the polygon count by removing some vertices with best preset settings which means highest reduction but good quality\n
        surfacicTolerance = 1.0\n
        lineicTolerance = 0.1\n
        normalTolerance = 5.0\n
        texCoordTolerance = -1\n
        releaseConstraintOnSmallArea = False\n

        - Parameters: \n
            - occurrences (OccurrenceList) : Occurrences of components to process\n
        - Returns:\n
            - void\n

        """
        if self.verbose:
            Logger('before decimate').PrintModelInfo(self.root)

        if len(occurrences) == 0:
            occurrences = [self.root]

        self.Decimate(occurrences, 1.0, 0.1, 5.0, -1, False)

    def DecimateTarget(self, occurrences = [], targetStrategy = ["ratio", 75], boundaryWeight = 0.0, normalWeight = 1.0, UVWeight = 0.0, sharpNormalWeight = 0.0, UVSeamWeight = 0.0, forbidUVFoldovers = False, protectTopology = True):
        """
        Reduce the polygon count by collapsing some edges to obtain a target triangle count

        - Parameters: \n
            - occurrences (OccurrenceList) : List of occurrences to process\n
            - TargetStrategy (DecimateOptionsSelector) : Select between targetCount or ratio to define the number of triangles left after the decimation process\n
            - boundaryWeight (Double) [optional] : Defines how important the edges defining the mesh boundaries (free edges) are during the decimation process, to preserve them from distortion\n
            - normalWeight (Double) [optional] : Defines how important vertex normals are during the decimation process, to preserve the smoothing of the mesh from being damaged\n
            - UVWeight (Double) [optional] : Defines how important UVs (texture coordinates) are during the decimation process, to preserve them from being distorted (along with the textures using the UVs)\n
            - sharpNormalWeight (Double) [optional] : Defines how important sharp edges (or hard edges) are during the decimation process, to preserve them from being distorted\n
            - UVSeamWeight (Double) [optional] : Defines how important UV seams (UV islands contours) are during the decimation process, to preserve them from being distorted (along with the textures using the UVs)\n
            - forbidUVFoldovers (Boolean) [optional] : Forbids UVs to fold over and overlap each other during the decimation\n
            - protectTopology (Boolean) [optional] : If False, the topology of the mesh can change and some edges can become non-manifold; but the visual quality will be better on model with complex topology\n
        - Returns:\n
            - void\n

        """
        # Logger(f"before decimateTarget - r:{targetStrategy[1]}").PrintOccurrenceInfo(occurrences)
        algo.decimateTarget(occurrences, targetStrategy, boundaryWeight, normalWeight, UVWeight, sharpNormalWeight, UVSeamWeight, forbidUVFoldovers, protectTopology)
        # Logger(f"after decimateTarget - r:{targetStrategy[1]}").PrintOccurrenceInfo(occurrences)