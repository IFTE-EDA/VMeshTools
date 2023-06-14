import PyVMAP as VMAP
import vedo as v
import os
import numpy as np
from .VMAPMeshReader import VMAPMeshReader

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


    def getFile(self, path: str, newName=""):
        arr = path.strip("/").split("/")
        group = "/" + "/".join(arr[:-1])
        dataset = arr[-1]
        # print ("{} - {}".format(group, dataset))
        if newName == "":
            file = self.vmap.getStringAttribute(path, "FILENAME")
            print("Saving File in {} to {}".format(group + "/" + dataset, file))
            ret = self.vmap.restoreExternalFile(group, dataset, file)
            print(newName, ret)
        else:
            print("Saving File in {} to {}".format(group+"/"+dataset, newName))
            ret = self.vmap.restoreExternalFile(group, dataset, newName)
            print(newName, ret)

    def storeFile(self, path: str, file: str, desc: str):
        arr = path.strip("/").split("/")
        group = "/" + "/".join(arr[:-1])
        dataset = arr[-1]
        #print ("{} - {}".format(group, dataset))
        self.vmap.saveExternalFile(group, dataset, file)
        #self.vmap.createStringAttribute(group, dataset, file)



class VMAPGroup:
    def __init__(self, handler, path):
        self.handler = handler
        self.path = path
        self.id = path.split("/")[-1]

    def __repr__(self):
        return "<VMAP subgroup '{}' at {}>".format(self.id, self.path)

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

    def isVMAPRoot(self):
        if self.id == "VMAP":
            children = self.getSubgroupNames()
            return all(x in children for x in ["GEOMETRY", "MATERIAL", "SYSTEM", "VARIABLES"])
        return False

    def isGeometrySection(self):
        return self.id == "GEOMETRY" and self.parent().id == "VMAP"

    def isMaterialSection(self):
        return self.id == "MATERIAL" and self.parent().id == "VMAP"

    def isSystemSection(self):
        return self.id == "SYSTEM" and self.parent().id == "VMAP"

    def isVariablesSection(self):
        return self.id == "VARIABLES" and self.parent().id == "VMAP"

    def isMeshGroup(self):
        return self.parent().isGeometrySection()  # name == "GEOMETRY" and self.parent().parent().id == "VMAP"

    def isMaterialGroup(self):
        return self.parent().isMaterialSection()

    def isSystemGroup(self):
        return self.parent().isSystemSection()

    def isVariablesGroup(self):
        return self.parent().isVariablesSection()


class VMAPMeshGroup(VMAPGroup):

    def __init__(self, handler, path):
        super().__init__(handler, path)

        if not self.exists():
            self.handler.vmap.createGroup(path)

        if not self.isMeshGroup():
            raise Exception("{} is no mesh group!".format(self))

        self.pointsRead = False
        self.pointIDsRead = False
        self.elementsRead = False
        self.elemTypesRead = False
        self.pointsParsed = False
        self.elementsParsed = False
        self.vmapRootPath = self.getNextVMAPRoot().parent().path

        #self.handler.pause()
        if self.vmapRootPath == "/":
            #print("Opening without rootpath")
            self.vmapRoot = VMAP.VMAPFile(self.handler.filename, VMAP.VMAPFile.OPENREADWRITE)
        else:
            self.vmapRootPath = self.vmapRootPath + "/VMAP/"
            #print("Opening with rootpath '{}'".format(self.vmapRootPath))
            self.vmapRoot = VMAP.VMAPFile(self.handler.filename, VMAP.VMAPFile.OPENREADWRITE, self.vmapRootPath)

        try:
            self.name = self.vmapRoot.getStringAttribute(path, "MYNAME")
        except RuntimeError:
            self.name = self.id
            print("No 'MYNAME' Attribute found in", self.path)
        self.getElements()

        #self.handler.resume()


    def __repr__(self):
        return "<VMAP geometry group '{}' with name '{}' at {}>".format(self.id, self.name, self.path)

    def getPointBlock(self, update=False):
        if not self.pointsRead or update:
            self.pointBlock = VMAP.sPointsBlock()   #TODO get length
            self.vmapRoot.readPointsBlock(self.path, self.pointBlock)
            self.pointsRead = True
            self.pointsParsed = False
            self.elementsRead = False
            self.elementsParsed = False
        return self.pointBlock

    def getPoints(self, update=False):
        if not self.pointsParsed or update:
            self.getPointBlock(update)
            self.points = np.reshape(self.pointBlock.myCoordinates, (-1, 3))
            self.pointsParsed = True
            self.elementsRead = False
            self.elementsParsed = False
        return self.points

    def getPointIDs(self, update=False):
        if not self.pointIDsRead or update:
            if not self.pointsRead:
                self.getPointBlock(update)
            self.pointIDs = dict.fromkeys((range(self.pointBlock.mySize)))
            self.pointIDs = {self.pointBlock.myIdentifiers[i]: i for i in range(self.pointBlock.mySize)}
            self.pointIDsRead = True
            self.elementsRead = False
            self.elementsParsed = False
        return self.pointIDs

    def getElementBlock(self, update=False):
        if not self.elementsRead or update:
            self.elementBlock = VMAP.sElementBlock()
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
            self.elementsRead = False
            self.elementsParsed = False
            #print("Found {} element types in {}".format(self.elemTypes.size(), self.vmapRootPath))
        return self.elemTypes

    def getElements(self, update=False):
        if not self.elementsParsed or update:
            if not self.elementsRead:
                self.getElementBlock(update)
            if not self.elemTypesRead:
                self.getElementTypes(update)
            if not self.pointsRead:
                self.getPoints(update)
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
        if not self.elemTypesRead:
            self.getElementTypes()
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
        if not self.pointIDsRead:
            self.getPointIDs()
        return self.pointIDs[id]
        #return id-1

    def getPointFromID(self, id):
        return self.points[self.pointIDs[id]]

    def getPointsFromConn(self, conn, ids):
        return [self.getPointIndexFromID(conn[i]) for i in ids]




    def __makePointBlock(self, mesh):
        block = VMAP.sPointsBlock(mesh.NPoints())
        pts = mesh.points()
        for i in range(mesh.NPoints()):
            #print("{}: {}/{}/{}; {}".format(i+1, pts[i][0], pts[i][1], pts[i][2], type(pts[i][0])))
            block.setPoint(i, i+1, float(pts[i][0]), float(pts[i][1]), float(pts[i][2]))
        return block

    def __makeElementsBlock(self, mesh):
        block = VMAP.sElementBlock(mesh.NCells())
        faces = mesh.faces()
        for i, face in enumerate(faces):
            #print("Face: {}".format(face))
            conn = [int(i+1) for i in face]
            elem = VMAP.sElement(3)
            elem.myIdentifier = i+1
            elem.myElementType = 1
            elem.myCoordinateSystem = 1         # TODO
            elem.myMaterialType = 1             # TODO
            #print("Conn: {}".format(conn))
            elem.setConnectivity(conn)

            block.setElement(i, elem)

        return block

    def __elemTypeDefined(self):
        type = self.getElementTypeFromId(1)
        conn = type.getConnectivity()
        if type.myShapeType == VMAP.sElementType.TRIANGLE_3 and conn == (0, 1, 2):
            return True
        else:
            return False

    def __makeElementTypes(self):
        type = VMAP.sElementType()
        type.myIdentifier = 1
        type.myTypeName = "TRIANGLE_3"
        type.myTypeDescription = "TRIANGLE_3"
        type.myNumberOfNodes = 3
        type.myDimension = 2
        type.myShapeType = VMAP.sElementType.TRIANGLE_3
        #type.myInterpolationType
        #type.myIntegrationType
        #type.myNumberOfNormalComponents
        #type.myNumberOfShearComponents
        type.setConnectivity([0, 1, 2])
        #faceConn = [2, 3, 0, 1, 2, 3, 0, 2, 1]
        type.setFaceConnectivity ([2, 3, 0, 1, 2, 3, 0, 2, 1])
        return [type]

    def writeMesh_vedo(self, mesh: str, name=""):
        print("Writing PointBlock")
        #self.handler.vmap.writePointsBlock(self.path, pb)
        self.vmapRoot.writePointsBlock(self.path, self.__makePointBlock(mesh))
        #self.handler.vmap.writeElementsBlock(self.path, self.__makeElementsBlock(mesh))
        self.vmapRoot.writeElementsBlock(self.path, self.__makeElementsBlock(mesh))
        if not name == "":
            self.vmapRoot.createStringAttribute(self.path, "MYNAME", name)
        if not self.__elemTypeDefined():
            self.vmapRoot.writeElementTypes(self.__makeElementTypes())
        self.elementsWritten = True





    def renderMesh_vedo(self):
        faces, tets = self.getElements()
        mesh = v.Mesh([self.points, self.faces]).c("red").alpha(1).lw(1) if len(self.faces) > 0 else v.TetMesh([self.points, self.tets], mapper='tetra').tomesh(fill=False).c("red").alpha(1)
        return mesh

    def renderPointcloud_vedo(self):
        #mesh = v.Mesh([self.points, self.faces]).c("red").alpha(1).lw(1) if len(self.faces) > 0 else v.TetMesh([self.points, self.tets], mapper='tetra').tomesh(fill=False).c("red").alpha(1)
        pcld = v.Points(self.getPoints() , c="blue").ps(3)
        return pcld

    def show(self):
        v.show(self.renderMesh_vedo())




class VMAPMaterialGroup(VMAPGroup):

    def __init__(self, handler, path):
        super().__init__(handler, path)

        if self.exists():       #group exists, load data
            if not self.isMaterialGroup():
                raise Exception("{} is no material group!".format(self))
            self.matId = int(self.id)
            self.mat = VMAP.sMaterial()
            #self.matCard = VMAP.sMaterialCard()
            self.handler.vmap.readMaterial(self.path, self.mat)
            self.matCardRaw = self.mat.getMaterialCard()
            self.matName = self.mat.getMaterialName()
            self.matDesc = self.mat.getMaterialDescription()
            self.matState = self.mat.getMaterialState()
            self.matSupplier = self.mat.getMaterialSupplier()
            self.matType = self.mat.getMaterialType()

            self.matCard = dict()
            self.matCard["modelName"] = self.matCardRaw.getModelName()
            self.matCard["identifier"] = self.matCardRaw.getIdentifier()
            self.matCard["physics"] = self.matCardRaw.getPhysics()
            self.matCard["solver"] = self.matCardRaw.getSolver()
            self.matCard["solverVersion"] = self.matCardRaw.getSolverVersion()
            self.matCard["solution"] = self.matCardRaw.getSolution()
            self.matCard["unitSystem"] = self.matCardRaw.getUnitSystem()
            self.matCard["idealization"] = self.matCardRaw.getIdealization()

            self.paramRaw = self.matCardRaw.getParameters()
            self.param = {p.getName(): p.getValue() for p in self.paramRaw}
            self.paramDesc = {p.getName(): p.getDescription() for p in self.paramRaw}




            self.setColor(self.param["DisplayColor"])
        else:                   #load default values
            self.color = [128, 128, 128, 0]


        self.vmapRootPath = self.getNextVMAPRoot().parent().path

        """if self.vmapRootPath == "/":
            self.vmapRoot = VMAP.VMAPFile(self.handler.filename, VMAP.VMAPFile.OPENREADONLY)
        else:
            self.vmapRoot = VMAP.VMAPFile(self.handler.filename, VMAP.VMAPFile.OPENREADONLY, self.vmapRootPath)
        """

    def __repr__(self):
        return "<VMAP material group '{}' at {}>".format(self.id, self.path)

    def setColor(self, col, alpha=255):
        if type(col) is str:    #hexcode
            if len(col) == 6:
                self.color = tuple(int(col[i:i+2], 16) for i in (0, 2, 4))
                self.alpha = alpha
            elif len(col) == 8:
                self.color = tuple(int(col[i:i + 2], 16) for i in (0, 2, 4, 6))
            else:
                raise AttributeError("Unrecognized color string:", col)
        else:
            if alpha == 0 and len(col) == 4:
                self.color = col[0:2]
            elif len(col) == 3:
                self.color = color
                self.color[3] = alpha
            else:
                raise AttributeError("Wrong arguments for VMAPMaterialGroup.setColor: col={}, alpha={}".format(col, alpha))