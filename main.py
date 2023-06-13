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

        print("#Meshes: ", vh.getNMeshes(geom.path), geom1)
        print("\n\n\n")
        geom1 = vh.getMeshes(geom.path)

        print("Geom1:", geom1)
        #geom1 = geom.getMesh()


        print("Subgrouping VMAP root:")
        sub = vh.getSubgroup("/VMAP")
        print ("IsVMAPRoot:", sub.isVMAPRoot())
        print("NextVMAPRoot of Geom:", sub.getNextVMAPRoot())
        #print("NextVMAPRoot of wrong dir:", vh.getSubgroup("test/dir/subdir/thereIsNoVMAPHere").getNextVMAPRoot())
        for mesh in geom1:
            print("Mesh: ", mesh)
            print("Points: ", len(mesh.points))
            print("Faces: ", len(mesh.faces))
            print("Tets: ", len(mesh.tets))
        mesh1 = geom1[0].renderPointcloud_vedo()
        mesh2 = geom1[1].renderMesh_vedo()
        boat = v.Mesh("test/ben_floating_benchmark.stl")
        VMAPMeshGroup(vh, "/VMAP/GEOMETRY/5").writeMesh_vedo(boat)
        #geom1[2].getElements(True)
        mesh3 = geom1[2].renderMesh_vedo()
        mesh3 = VMAPMeshGroup(vh, "/VMAP/GEOMETRY/5").renderMesh_vedo()

        #print(vh.getProcessStepNames())
        mesh4 = vh.getMeshes("/1_Firststep/VMAP/GEOMETRY")[0].renderMesh_vedo()
        mesh5 = vh.getMeshes("/2_Secondstep/VMAP/GEOMETRY")[0].renderMesh_vedo()
        mesh6 = vh.getMeshes("/3_Thirdstep/VMAP/GEOMETRY")[0].renderMesh_vedo()
        print("Loading PLA mat...")
        mPLA = VMAPMaterialGroup(vh, "1_Firststep/VMAP/MATERIAL/1")
        print("Loading Cu mat...")
        mCu = VMAPMaterialGroup(vh, "3_Thirdstep/VMAP/MATERIAL/1")
        v.show(mesh1.x(-100), mesh2, mesh3.x(100), mesh4.y(-200).x(-100), mesh5.y(-200), mesh6.y(-200).x(100))



#print(timeit.timeit("main()", number=1))
#print(timeit.Timer(main).timeit(number=1))
main()
