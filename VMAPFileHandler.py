import PyVMAP as VMAP
import vedo as v
import os
import numpy as np
from VMAPMeshReader import VMAPMeshReader

class VMAPFileHandler:

    def __init__(self, filename: str, mode=VMAP.VMAPFile.OPENREADWRITE):
        self.filename = filename
        self.vmap = VMAP.VMAPFile(filename, mode)
        #self.vmap.createGroup("/test/dir/subdir/thereIsNoVMAPHere")

    def pause(self):
        self.vmap.closeFile()

    def resume(self):
        self.vmap.openFile(self.filename)

    def getSubgroup(self, path: str, groupType=None):
        if groupType is None:
            return VMAPGroup(self, path)
        else:
            return groupType(self, path)

    def getNSubgroups(self, path: str):
        return len(self.vmap.getSubGroups(path))

    def getSubgroups(self, path: str, groupType=None):
        return [self.getSubgroup(path, groupType) for path in self.getSubgroupPaths(path)]

    def getSubgroupNames(self, path: str):
        return self.vmap.getSubGroups(path)

    def getSubgroupPaths(self, path: str):
        return self.vmap.getSubGroupsPath(path)

    def subgroupExists(self, path):
        return self.vmap.existsGroup(path)

    def getNProcessSteps(self):
        return len(self.vmap.getSubGroups("/"))

    def getProcessSteps(self):
        return [VMAPGroup(self, path) for path in self.getSubgroupPaths("/")]

    def getProcessStepNames(self):
        return self.vmap.getSubGroups("/")

    def getProcessStepPaths(self):
        return self.vmap.getSubGroupsPath("/")

    def getNMeshes(self, path: str):
        grp = self.getSubgroup(path)
        if not grp.isGeometrySection():
            raise Exception("Path '{}' is no geometry section.".format(path))
        return self.getNSubgroups(path)

    def getMeshes(self, path: str):
        grp = self.getSubgroup(path)
        if not grp.isGeometrySection():
            raise Exception("Path '{}' is no geometry section.".format(path))
        return self.getSubgroups(path, VMAPMeshGroup)

    def getMeshNames(self, path: str):
        pass

    def getMeshPaths(self, path: str):
        pass


    def getFile(self, path: str):
        pass

    def storeFile(self, path: str, file, description: str):
        pass


class VMAPGroup:
    def __init__(self, handler, path):
        self.handler = handler
        self.path = path
        self.name = path.split("/")[-1]

    def __repr__(self):
        return "<VMAP subgroup '{}' at {}>".format(self.name, self.path)

    def exists(self):
        return self.handler.subgroupExists(self.path)
    def getNSubgroups(self):
        return self.handler.getNSubgroups(self.path)

    def getSubgroups(self):
        return self.handler.getSubgroups(self.path)

    def getSubgroupNames(self):
        return self.handler.getSubgroupNames(self.path)

    def subgroupExists(self, path):
        return self.handler.subgroupExists(os.path.join(self.path, name))

    def parent(self):
        return self.handler.getSubgroup(os.path.dirname(self.path))

    def getNextVMAPRoot(self):
        #print("Parsing next VMAP Root of", self)
        root = self
        while (not root.isVMAPRoot()):
            root = root.parent()
            if root.path == "":
                return None
        #print("Found root:", root)
        return root

    def subgroup(self, name):
        return self.handler.getSubgroup(self.path + "/" + name)

    def isMeshGroup(self):
        return self.parent().name == "GEOMETRY" and self.parent().parent().name == "VMAP"

    def isGeometrySection(self):
        return self.name == "GEOMETRY" and self.parent().name == "VMAP"

    def isMaterialSection(self):
        return self.name == "MATERIAL" and self.parent().name == "VMAP"

    def isSystemSection(self):
        return self.name == "SYSTEM" and self.parent().name == "VMAP"

    def isVariablesSection(self):
        return self.name == "VARIABLES" and self.parent().name == "VMAP"

    def isVMAPRoot(self):
        if self.name == "VMAP":
            children = self.getSubgroupNames()
            return all(x in children for x in ["GEOMETRY", "MATERIAL", "SYSTEM", "VARIABLES"])
        return False

class VMAPMeshGroup(VMAPGroup):

    def __init__(self, handler, path):
        super().__init__(handler, path)

        self.pointsRead = False
        self.pointIDsRead = False
        self.elementsRead = False
        self.elemTypesRead = False
        self.pointsParsed = False
        self.elementsParsed = False
        self.vmapRootPath = self.getNextVMAPRoot().parent().path

        #self.handler.pause()
        if self.vmapRootPath == "/":
            self.vmapRoot = VMAP.VMAPFile(self.handler.filename, VMAP.VMAPFile.OPENREADONLY)
        else:
            self.vmapRoot = VMAP.VMAPFile(self.handler.filename, VMAP.VMAPFile.OPENREADONLY, self.vmapRootPath)

        print("Points: ", len(self.getPoints()))
        print("PointIDs: ", len(self.getPointIDs()))
        print("ElemTypes: ", len([i for i in self.getElementTypes()]))
        print("Elements: ", len(self.getElements()))
        print("\n")

        #self.handler.resume()


    def __repr__(self):
        return "<VMAP geometry group '{}' at {}>".format(self.name, self.path)

    def getPointBlock(self, update=False):
        if not self.pointsRead or update:
            self.pointBlock = VMAP.sPointsBlock()   #TODO get length
            self.vmapRoot.readPointsBlock(self.path, self.pointBlock)
            self.pointsRead = True
            self.pointsParsed = False
        return self.pointBlock

    def getPoints(self, update=False):
        if not self.pointsParsed or update:
            self.getPointBlock(update)
            self.points = np.reshape(self.pointBlock.myCoordinates, (-1, 3))
            self.pointsParsed = True
        return self.points

    def getPointIDs(self, update=False):
        if not self.pointIDsRead or update:
            if not self.pointsRead:
                self.getPointBlock(update)
            self.pointIDs = dict.fromkeys((range(self.pointBlock.mySize)))
            self.pointIDs = {self.pointBlock.myIdentifiers[i]: i for i in range(self.pointBlock.mySize)}
            self.pointIDsRead = True
        return self.pointIDs

    def getElementBlock(self, update=False):
        if not self.elementsRead or update:
            self.elementBlock = VMAP.sElementBlock()    #TODO gt length
            self.vmapRoot.readElementsBlock(self.path, self.elementBlock)
            self.elementsRead = True
            self.elementsParsed = False
        return self.elementBlock

    def getElementTypes(self, update=False):
        if not self.elemTypesRead or update:
            self.elemTypes = VMAP.VectorTemplateElementType()
            #self.handler.vmap.readElementTypes(self.elemTypes)
            self.vmapRoot.readElementTypes(self.elemTypes)
            self.elemTypesRead = True
            #print("Found {} element types in {}".format(self.elemTypes.size(), self.vmapRootPath))
        return self.elemTypes

    def getElements(self, update=False):
        if not self.elementsParsed or update:
            if not self.elementsRead:
                self.getElementBlock(update)
            faces = []
            tets = []
            for i in range(self.elementBlock.myElementsSize):
                elem = self.elementBlock.getElement(i)
                conn = elem.getConnectivity()
                elemType = self.getElementTypeFromId(
                    elem.getElementType()).getShapeType()  # elemTypes[elem.getElementType()-1]
                # elemType = self.elemTypes[elem[1]]
                if elemType in [VMAP.sElementType.TRIANGLE_3, VMAP.sElementType.TRIANGLE_4,
                                VMAP.sElementType.TRIANGLE_6]:
                    faces.append(self.getPointsFromConn(conn, [0, 1, 2]))
                elif elemType in [VMAP.sElementType.QUAD_4, VMAP.sElementType.QUAD_8, VMAP.sElementType.QUAD_9]:
                    faces.append(self.getPointsFromConn(elem, [0, 1, 2, 3]))
                elif elemType in [VMAP.sElementType.TETRAHEDRON_4, VMAP.sElementType.TETRAHEDRON_5,
                                  VMAP.sElementType.TETRAHEDRON_10, VMAP.sElementType.TETRAHEDRON_11]:
                    tets.append(self.getPointsFromConn(elem, [0, 1, 2, 3]))
                elif elemType in [VMAP.sElementType.PYRAMID_5, VMAP.sElementType.PYRAMID_6,
                                  VMAP.sElementType.PYRAMID_13]:
                    tets.append(self.getPointsFromElement(elem, [0, 1, 2, 4]))
                    tets.append(self.getPointsFromElement(elem, [0, 2, 3, 4]))
                elif elemType in [VMAP.sElementType.HEXAHEDRON_8, VMAP.sElementType.HEXAHEDRON_9,
                                  VMAP.sElementType.HEXAHEDRON_20, VMAP.sElementType.HEXAHEDRON_21,
                                  VMAP.sElementType.HEXAHEDRON_27]:
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
                    raise NotImplementedError(
                        "Element type not imlemented: {} in element #{}".format(elemType, elem.getIdentifier()))
            self.faces = faces
            self.tets = tets
        return (self.faces, self.tets)

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

    def getPointIndexFromID(self, id):  #TODO: test for easier adressing via i=id-1; recorrect first to ict-like lookup
        return self.pointIDs[id]
        #return id-1

    def getPointFromID(self, id):
        return self.points[self.pointIDs[id]]

    def getPointsFromConn(self, conn, ids):
        return [self.getPointIndexFromID(conn[i]) for i in ids]

    def renderMesh_vedo(self):
        mesh = v.Mesh([self.points, self.faces]).c("red").alpha(1).lw(1) if len(self.faces) > 0 else v.TetMesh([self.points, self.tets], mapper='tetra').tomesh(fill=False).c("red").alpha(1)
        pcld = v.Points(self.points, c="blue").ps(3)
        return mesh  # , pcld#mesh

    def show(self):
        v.show(self.renderMesh_vedo())