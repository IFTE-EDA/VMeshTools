import PyVMAP as VMAP
import vedo as v


class VMAPMeshWriter:
    elemTypes = {}
    points = []
    elements = []
    pointIDs = {}

    def __init__(self, file):
        self.vmap = file
        self.elementsWritten = False

    @staticmethod
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

    def getPointBlock(self, mesh):
        block = VMAP.sPointsBlock(mesh.NPoints())
        pts = mesh.points()
        for i in range(mesh.NPoints()):
            #print("{}: {}/{}/{}; {}".format(i+1, pts[i][0], pts[i][1], pts[i][2], type(pts[i][0])))
            block.setPoint(i, i+1, float(pts[i][0]), float(pts[i][1]), float(pts[i][2]))
        return block

    def getElementsBlock(self, mesh):
        block = VMAP.sElementBlock(mesh.NCells())
        faces = mesh.faces()
        for i, face in enumerate(faces):
            #print("Face: {}".format(face))
            conn = [int(i+1) for i in face]
            elem = VMAP.sElement(3)
            elem.myIdentifier = i+1
            elem.myElementType = 1
            elem.myCoordinateSystem = 1
            elem.myMaterialType = 1
            #print("Conn: {}".format(conn))
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
        type.myShapeType = VMAP.sElementType.TRIANGLE_3
        #type.myInterpolationType
        #type.myIntegrationType
        #type.myNumberOfNormalComponents
        #type.myNumberOfShearComponents
        type.setConnectivity([0, 1, 2])
        #faceConn = [2, 3, 0, 1, 2, 3, 0, 2, 1]
        type.setFaceConnectivity ([2, 3, 0, 1, 2, 3, 0, 2, 1])
        return [type]

    def writeMeshToFile(self, mesh: v.Mesh, path: str, name: str):
        #if str == "":
        #    file.
        print("Writing PointBlock")
        self.vmap.writePointsBlock(path, self.getPointBlock(mesh))
        print("Writing ElementBlock")
        self.vmap.writeElementsBlock(path, self.getElementsBlock(mesh))
        if not self.elementsWritten:
            self.vmap.writeElementTypes(self.getElementTypes())
            self.elementsWritten = True
