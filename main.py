import numpy as np

import PyVMAP as VMAP

import vedo as v
from VMAPMeshWriter import VMAPMeshWriter
from VMAPMeshReader import VMAPMeshReader

if __name__ == '__main__':
    print("VMAP Mesh Tester")
    VMAP.Initialize()
    """metaInfo = VMAP.sMetaInformation()
    metaInfo.setExporterName("pythoninterface")
    metaInfo.setFileDate("20230605")
    metaInfo.setFileTime("12:00:00")
    metaInfo.setDescription("First test of writing a STL to a file\n")
    """

    print("Opening...")
    file = VMAP.VMAPFile("STLWTest.h5", VMAP.VMAPFile.OPENREADONLY)
    """file = VMAP.VMAPFile("STLWTest.h5")
    file.writeMetaInformation(metaInfo)

    print("Initializing UnitSystem")

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

    bunny = v.Mesh("test/Stanford_Bunny.stl")
    writer = VMAPMeshWriter(bunny)
    writer.writeMeshToFile(file, "VMAP/GEOMETRY/1", "MyMesh")
    """
    print("Reading...")
    reader = VMAPMeshReader(file, "VMAP/GEOMETRY/1")
    v.show(reader.getMesh())
    """
    pointBlock = writer.getPointBlock()
    file.writePointsBlock("VMAP/GEOMETRY/1", pointBlock)
    elemBlock = writer.getElementsBlock()
    file.writeElementsBlock("VMAP/GEOMETRY/1", elemBlock)
    type = writer.getElementTypes()
    file.writeElementTypes([type])
    """

