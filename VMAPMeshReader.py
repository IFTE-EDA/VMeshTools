import VMAPMeshTools
import PyVMAP as VMAP
import vedo as v
import numpy as np
from enum import Enum

class VMAPMeshReader:

    def __init__(self, vmap: VMAP.VMAPFile, path: str):
        self.vmap = vmap
        #points, elements, elemTypes = [], [], []
        self.pointBlock = VMAP.sPointsBlock()
        self.pointIDs = dict.fromkeys((range(self.pointBlock.mySize)))
        self.elementBlock = VMAP.sElementBlock()
        self.elemTypes = VMAP.VectorTemplateElementType()
        vmap.readPointsBlock(path, self.pointBlock)
        vmap.readElementsBlock(path, self.elementBlock)
        vmap.readElementTypes(self.elemTypes)

        self.points = np.reshape(self.pointBlock.myCoordinates, (-1, 3))
        self.pointIDs = {self.pointBlock.myIdentifiers[i]: i for i in range(self.pointBlock.mySize)}

    def getElementTypeFromId(self, id: int):
        type = self.elemTypes[id-1]
        if type.getIdentifier() != id:          #not numbered as ID(i)=i+1... =(
            print("ID {} not found. Searching...".format(id))
            for eType in self.elemTypes:
                if eType.getIdentifier() == id:
                    type = eType
        if type.getIdentifier() == id:
            return type
        else:
            raise Exception("Element type identifier not found: {}".format(id))


    def setPoints(self, points):
        self.points = points

    def setIDs(self, ids):
        self.pointIDs = {id: i for i, id in enumerate(ids)}

    def setElements(self, elements):
        self.elements = elements

    def setElementTypes(self, elemTypes):
        self.elemTypes = {elem[0]: elem[5] for i, elem in enumerate(elemTypes)}

    def getPointIndexFromID(self, id):  #TODO: test for easier adressing via i=id-1; recorrect first to ict-like lookup
        return self.pointIDs[id]
        #return id-1

    def getPointFromID(self, id):
        return self.points[self.pointIDs[id]]

    def getPointsFromConn(self, conn, ids):
        return [self.getPointIndexFromID(conn[i]) for i in ids]

    def getMesh(self):
        faces = []
        tets = []
        for i in range(self.elementBlock.myElementsSize):
            elem = self.elementBlock.getElement(i)
            conn = elem.getConnectivity()
            elemType = self.getElementTypeFromId(elem.getElementType()).getShapeType()  # elemTypes[elem.getElementType()-1]
            #elemType = self.elemTypes[elem[1]]
            if elemType in [VMAP.sElementType.TRIANGLE_3, VMAP.sElementType.TRIANGLE_4, VMAP.sElementType.TRIANGLE_6]:
                faces.append(self.getPointsFromConn(conn, [0, 1, 2]))
            elif elemType in [VMAP.sElementType.QUAD_4, VMAP.sElementType.QUAD_8, VMAP.sElementType.QUAD_9]:
                faces.append(self.getPointsFromConn(elem, [0, 1, 2, 3]))
            elif elemType in [VMAP.sElementType.TETRAHEDRON_4, VMAP.sElementType.TETRAHEDRON_5, VMAP.sElementType.TETRAHEDRON_10, VMAP.sElementType.TETRAHEDRON_11]:
                tets.append(self.getPointsFromConn(elem, [0, 1, 2, 3]))
            elif elemType in [VMAP.sElementType.PYRAMID_5, VMAP.sElementType.PYRAMID_6,VMAP.sElementType.PYRAMID_13]:
                tets.append(self.getPointsFromElement(elem, [0, 1, 2, 4]))
                tets.append(self.getPointsFromElement(elem, [0, 2, 3, 4]))
            elif elemType in [VMAP.sElementType.HEXAHEDRON_8, VMAP.sElementType.HEXAHEDRON_9, VMAP.sElementType.HEXAHEDRON_20, VMAP.sElementType.HEXAHEDRON_21, VMAP.sElementType.HEXAHEDRON_27]:
                tets.append(self.getPointsFromElement(elem, [0, 1, 2, 5]))
                tets.append(self.getPointsFromElement(elem, [0, 2, 3, 7]))
                tets.append(self.getPointsFromElement(elem, [0, 4, 5, 7]))
                tets.append(self.getPointsFromElement(elem, [2, 5, 6, 7]))
                tets.append(self.getPointsFromElement(elem, [1, 3, 4, 6]))
            elif elemType in [VMAP.sElementType.WEDGE_6, VMAP.sElementType.WEDGE_15]:
                tets.append(self.getPointsFromElement(elem, [0, 1, 2, 3]))
                tets.append(self.getPointsFromElement(elem, [2, 3, 4, 5]))
                tets.append(self.getPointsFromElement(elem, [1, 2, 3, 4]))
            else:
                raise NotImplementedError("Element type not imlemented: {} in element #{}".format(elemType, elem.getIdentifier()))
        mesh = v.Mesh([self.points, faces]).c("red").alpha(1).lw(1) if len(faces) > 0 else v.TetMesh([self.points, tets], mapper='tetra').tomesh(fill=False).c("red").alpha(1)
        pcld = v.Points(self.points, c="blue").ps(3)
        return mesh, pcld#mesh
            
        
        