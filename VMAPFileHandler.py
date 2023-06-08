import PyVMAP as VMAP
import vedo as v
import os


class VMAPFileHandler:

    def __init__(self, filename: str, mode=VMAP.VMAPFile.OPENREADONLY):
        self.vmap = VMAP.VMAPFile("STLWTest.h5", mode)

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
        self.handler.getNSubgroups(self.path)

    def getSubgroups(self):
        self.handler.getSubgroups(self.path)

    def getSubgroupNames(self):
        self.handler.getSubgroupsNames(self.path)

    def subgroupExists(self, path):
        return self.handler.subgroupExists(os.path.join(self.path, name))

    def parent(self):
        return self.handler.getSubgroup(os.path.dirname(self.path))

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


class VMAPMeshGroup(VMAPGroup):

    def __init__(self, handler, path):
        super().__init__(handler, path)
    def __repr__(self):
        return "<VMAP geometry group '{}' at {}>".format(self.name, self.path)

    def renderVedo(self):
        pass