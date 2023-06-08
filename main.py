import timeit
import numpy as np

import PyVMAP as VMAP

import vedo as v
from VMAPMeshWriter import VMAPMeshWriter
from VMAPMeshReader import VMAPMeshReader
from VMAPFileHandler import *

def main():
    if __name__ == '__main__':
        print("VMAP Mesh Tester")
        VMAP.Initialize()
        print("Opening...")
        #file = VMAPMeshWriter.getEmptyVMAPFile("STLWTest.h5")
        #file = VMAP.VMAPFile("STLWTest.h5")

        vh = VMAPFileHandler("STLWTest.h5")
        print(vh.getNProcessSteps())
        print(vh.getProcessStepPaths())
        print(vh.getProcessStepNames())

        print(vh.getNSubgroups("/VMAP"))
        print(vh.getSubgroups("/VMAP"))
        print(vh.getSubgroupNames("/VMAP"))

        print(vh.getSubgroups("/VMAP/GEOMETRY/1")[0].parent())

        geom = vh.getSubgroup("/VMAP/GEOMETRY")
        geom1 = vh.getSubgroup("/VMAP/GEOMETRY/1")

        print(geom1)
        print(geom1.isMeshGroup())
        print(geom1.parent().isGeometrySection())
        sub = geom1.subgroup("POINTS")
        print(sub.exists())

        print("\n\n\n")

        geom1 = vh.getMeshes(geom.path)
        print("Meshes: ", vh.getNMeshes(geom.path), geom1)

        print(geom1)
        #geom1 = geom.getMesh()

        return
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

#print(timeit.timeit("main()", number=1))
#print(timeit.Timer(main).timeit(number=1))
main()
