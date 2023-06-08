import timeit
import numpy as np

import PyVMAP as VMAP

import vedo as v
from VMAPMeshWriter import VMAPMeshWriter
from VMAPMeshReader import VMAPMeshReader

def main():
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
        #file = VMAPMeshWriter.getEmptyVMAPFile("STLWTest.h5")
        """file.writeMetaInformation(metaInfo)
    
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
        """
        #file = VMAP.VMAPFile("STLWTest.h5")
        file = VMAPMeshWriter.getEmptyVMAPFile("STLWTest.h5")
        bunny = v.Mesh("test/Stanford_Bunny.stl")
        tower = v.Mesh("test/Eiffel_Tower.stl")
        gear = v.Mesh("test/Gear.stl")
        writer = VMAPMeshWriter(file)
        writer.writeMeshToFile(bunny, "VMAP/GEOMETRY/1", "Stanford Bunny")
        writer.writeMeshToFile(tower, "VMAP/GEOMETRY/2", "Eiffel Tower")
        writer.writeMeshToFile(gear, "VMAP/GEOMETRY/3", "Gear... sort of")
        file.closeFile()


        print("Reading...")
        file = VMAP.VMAPFile("STLWTest.h5", VMAP.VMAPFile.OPENREADONLY)
        bunnyReader = VMAPMeshReader(file, "VMAP/GEOMETRY/1")
        towerReader = VMAPMeshReader(file, "VMAP/GEOMETRY/2")
        gearReader = VMAPMeshReader(file, "VMAP/GEOMETRY/3")
        readBunny = bunnyReader.getMesh()
        readTower = towerReader.getMesh().x(-100)
        readGear = gearReader.getMesh().x(100)
        v.show(readBunny, readTower, readGear)
        """
        pointBlock = writer.getPointBlock()
        file.writePointsBlock("VMAP/GEOMETRY/1", pointBlock)
        elemBlock = writer.getElementsBlock()
        file.writeElementsBlock("VMAP/GEOMETRY/1", elemBlock)
        type = writer.getElementTypes()
        file.writeElementTypes([type])
        """

#print(timeit.timeit("main()", number=1))
#print(timeit.Timer(main).timeit(number=1))
main()
