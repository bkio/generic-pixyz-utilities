@0xc9bce8ec8ed176e9;

struct CPColor {
  r @0 :Float32;
  g @1 :Float32;
  b @2 :Float32;
}

struct CPVector3D {
  x @0 :Float32;
  y @1 :Float32;
  z @2 :Float32;
}

struct CPVertexNormalTangent {
  vertex @0 :CPVector3D;
  normal @1 :CPVector3D;
  tangent @2 :CPVector3D;
}

struct CPLOD {
  vertexNormalTangentList @0 :List(CPVertexNormalTangent);
  indexes @1: List(UInt32);
}

struct CPGeometryPart {
  geometryID @0 :UInt64;
  location @1 :CPVector3D;
  rotation @2 :CPVector3D;
  scale @3 :CPVector3D;
  color @4 :CPColor;
}

struct CPHierarchyNode {
  uniqueID @0 :UInt64;
  parentID @1 :UInt64;
  metadataID @2 :UInt64;
  geometryParts @3 :List(CPGeometryPart);
  childNodes @4 :List(UInt64);
}

struct CPMetadataNode {
  uniqueID @0 :UInt64;
  metadata @1 :Text;
}

struct CPGeometryNode {
  uniqueID @0 :UInt64;
  lodNumber @1 :Int32;
  lod @2 :CPLOD;
}

struct CPNodeMessage {
  modelID @0 :UInt64;
  errors @1 :List(Text);
  hierarchyNode @2 :CPHierarchyNode;
  metadataNode @3 :CPMetadataNode;
  geometryNode @4 :CPGeometryNode;
  done @5 :Bool;
  messageCount @6: Int32;
}