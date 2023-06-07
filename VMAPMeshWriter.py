import PyVMAP as VMAP
import vedo as v


class VMAPMeshWriter:
    elemTypes = {}
    points = []
    elements = []
    pointIDs = {}

    def __init__(self, mesh, attrs={}):
        self.mesh = mesh
        self.attrs = attrs

    """@staticmethod
    def getEmptyVMAPFile(fName: str):
        #VMAP.Initialize()
        file = VMAP.VMAPFile(fName)

        #metaInfo = VMAP.sMetaInformation()
        #metaInfo.setExporterName("pythoninterface")
        #metaInfo.setFileDate("20230605")
        #metaInfo.setFileTime("12:00:00")
        #metaInfo.setDescription("First test of writing a STL to a file\n")
        #file.writeMetaInformation(metaInfo)

        unitSystem = VMAP.sUnitSystem()
        unitSystem.getLengthUnit().setUnitSymbol("m")
        unitSystem.getMassUnit().setUnitSymbol("kg")
        unitSystem.getTimeUnit().setUnitSymbol("s")
        unitSystem.getCurrentUnit().setUnitSymbol("A")
        unitSystem.getTemperatureUnit().setUnitSymbol("K")
        unitSystem.getAmountOfSubstanceUnit().setUnitSymbol("mol")
        unitSystem.getLuminousIntensityUnit().setUnitSymbol("cd")
        file.writeUnitSystem(unitSystem)

        csystems = VMAP.VectorTemplateCoordinateSystem()
        csys = VMAP.sCoordinateSystem()
        csys.myIdentifier = 1
        csys.myType = VMAP.sCoordinateSystem.CARTESIAN_LEFT_HAND
        csys.setReferencePoint((0., 0., 0.))
        csys.setAxisVector(0, (1., 0., 0.))
        csys.setAxisVector(1, (0., 1., 0.))
        csys.setAxisVector(2, (0., 0., 1.))
        csystems.push_back(csys)
        file.writeCoordinateSystems("/VMAP/SYSTEM", csystems)
        return file
    """
    def getPointBlock(self):
        block = VMAP.sPointsBlock(self.mesh.NPoints())
        pts = self.mesh.points()
        for i in range(self.mesh.NPoints()):
            print("{}: {}/{}/{}; {}".format(i+1, pts[i][0], pts[i][1], pts[i][2], type(pts[i][0])))
            block.setPoint(i, i+1, float(pts[i][0]), float(pts[i][1]), float(pts[i][2]))
        return block

    def getElementsBlock(self):
        block = VMAP.sElementBlock(self.mesh.NCells())
        faces = self.mesh.faces()
        for i, face in enumerate(faces):
            print("Face: {}".format(face))
            conn = [int(i+1) for i in face]
            elem = VMAP.sElement(3)
            elem.myIdentifier = i+1
            elem.myElementType = 1
            elem.myCoordinateSystem = 1
            elem.myMaterialType = 1
            print("Face: {}".format(conn))
            elem.setConnectivity(conn)

            block.setElement(i, elem)

        return block

    def getElementTypes(self):
        type = VMAP.sElementType()
        type.myIdentifier = 1
        type.myTypeName = "TRIANGLE_3"
        type.myTypeDescription = "TRIANGLE_3"
        type.myNumberOfNodes = 3
        type.myDimension = 2
        type.myShapeType = vm.Shape.TRIANGLE_3
        #type.myInterpolationType
        #type.myIntegrationType
        #type.myNumberOfNormalComponents
        #type.myNumberOfShearComponents
        type.setConnectivity([0, 1, 2])
        #faceConn = [2, 3, 0, 1, 2, 3, 0, 2, 1]
        type.setFaceConnectivity ([2, 3, 0, 1, 2, 3, 0, 2, 1])
        return [type]

    def writeMeshToFile(self, file: VMAP.VMAPFile, path: str, name: str):
        #if str == "":
        #    file.
        file.writePointsBlock(path, self.getPointBlock())
        file.writeElementsBlock(path, self.getElementsBlock())
        file.writeElementTypes(self.getElementTypes())
