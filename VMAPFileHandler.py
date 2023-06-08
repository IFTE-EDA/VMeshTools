import PyVMAP as VMAP
import vedo as v
import os
from VMAPMeshReader import VMAPMeshReader

class VMAPFileHandler:

    def __init__(self, filename: str, mode=VMAP.VMAPFile.OPENREADWRITE):
        self.vmap = VMAP.VMAPFile("STLWTest.h5", mode)
        #self.vmap.createGroup("/test/dir/subdir/thereIsNoVMAPHere")

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
            raise Exception("Path '{}' is no mesh group.".format(path))
        return self.getNSubgroups(path)

    def getMeshes(self, path: str):
        grp = self.getSubgroup(path)
        if not grp.isGeometrySection():
            raise Exception("Path '{}' is no mesh group.".format(path))
        return self.getSubgroups(path, VMAPMeshGroup)#, VMAPMeshGroup)

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
        print("Parsing next VMAP Root.....")
        root = self
        while (not root.isVMAPRoot()):
            root = root.parent()
            if not root.path == "":
                return None
        print("Found root:", root)
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
            print(self.getSubgroupNames())
            children = self.getSubgroupNames()
            return all(x in children for x in ["GEOMETRY", "MATERIAL", "SYSTEM", "VARIABLES"])
        return False

class VMAPMeshGroup(VMAPGroup):

    def __init__(self, handler, path):
        super().__init__(handler, path)

        self.pointBlock = VMAP.sPointsBlock()
        self.elementBlock = VMAP.sElementBlock()
        self.elemTypes = VMAP.VectorTemplateElementType()
        self.pointsRead = False
        self.elementsRead = False
        self.elemTypesRead = False

        #print("Next root: ", self.getNextVMAPRoot())



        """vmap.readPointsBlock(path, self.pointBlock)
        vmap.readElementsBlock(path, self.elementBlock)
        vmap.readElementTypes(self.elemTypes)

        self.points = np.reshape(self.pointBlock.myCoordinates, (-1, 3))
        self.pointIDs = {self.pointBlock.myIdentifiers[i]: i for i in range(self.pointBlock.mySize)}
        """

    def __repr__(self):
        return "<VMAP geometry group '{}' at {}>".format(self.name, self.path)

    def getPoints(self, update=False):
        if not self.pointsRead or update:
            pass

    def getPointIDs(self, update=False):
        if not self.pointIDsRead or update:
            pass

    def getElements(self, update=False):
        if not self.elementsRead or update:
            pass

    def getElementTypes(self, update=False):
        if not self.elemTypesRead or update:
            self.pointIDs = dict.fromkeys((range(self.pointBlock.mySize)))

    def renderVedo(self):
        pass

    def show(self):
        pass