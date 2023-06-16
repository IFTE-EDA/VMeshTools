import pytest
import PyVMAP as VMAP
import VMeshTools as vmt
import os

print("Preparing Tests...")

@pytest.fixture
def testh5():
    print("Generating test HDF5 file...")

class Test_Tree:
    def setup_class(self):
        VMAP.Initialize()
        if not os.path.isfile("test/test.h5"):
            print ("'test/test.h5' not found; generating...")
            #execfile("createExampleFile.py")
            os.system("python createExampleFile.py")
        print("Opening 'test/test.h5'")
        self.vh = vmt.VMAPFileHandler("test/test.h5")

    def test_N_subgroups(self):
        assert self.vh.getNSubgroups("/") == 4

    def test_subgroups(self):
        assert self.vh.getSubgroups()[0].id == "1_Firststep"
        assert self.vh.getSubgroups()[1].id == "2_Secondstep"
        assert self.vh.getSubgroups()[2].id == "3_Thirdstep"
        assert self.vh.getSubgroups()[3].id == "VMAP"

    def test_subgroups_names(self):
        assert self.vh.getSubgroupNames()[0] == "1_Firststep"
        assert self.vh.getSubgroupNames()[1] == "2_Secondstep"
        assert self.vh.getSubgroupNames()[2] == "3_Thirdstep"
        assert self.vh.getSubgroupNames()[3] == "VMAP"

    def test_subgroups_paths(self):
        assert self.vh.getSubgroupPaths()[0] == "/1_Firststep"
        assert self.vh.getSubgroupPaths()[1] == "/2_Secondstep"
        assert self.vh.getSubgroupPaths()[2] == "/3_Thirdstep"
        assert self.vh.getSubgroupPaths()[3] == "/VMAP"

    def test_subgroups_exist(self):
        assert self.vh.subgroupExists("/VMAP")
        assert not self.vh.subgroupExists("/ThisIsNotReal")
        assert self.vh.subgroupExists("/1_Firststep/VMAP")
        assert not self.vh.subgroupExists("/1_Firststep/ThisIsNotReal")

    def test_N_process_steps(self):
        assert self.vh.getNProcessSteps() == 3

    def test_process_steps(self):
        assert str(self.vh.getProcessSteps()) == r"[<VMAP subgroup '1_Firststep' at /1_Firststep>, <VMAP subgroup '2_Secondstep' at /2_Secondstep>, <VMAP subgroup '3_Thirdstep' at /3_Thirdstep>]"      #TODO correct it, it's 3 actually

    def test_process_step_names(self):
        assert self.vh.getProcessStepNames() == ["1_Firststep", "2_Secondstep", "3_Thirdstep"]      #TODO correct it, it's 3 actually
        assert len(self.vh.getProcessSteps()) == 3

    def test_process_steps(self):
        assert self.vh.getProcessStepNames() == ["1_Firststep", "2_Secondstep", "3_Thirdstep"]      #TODO correct it, it's 3 actually
        assert len(self.vh.getProcessStepNames()) == 3



