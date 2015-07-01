
CXX = g++ -std=c++0x
CXXLIBS = -lmpi -lmpi++ -lmesh_devel
CXXINCLUDES = -I/usr/include/mpi

fem: introduction_ex4.C
	$(CXX) -o $@ $^ $(CXXLIBS) $(CXXINCLUDES)

macrofem: adaptivity_ex3.C trapmodel.C
	$(CXX) -o $@ $^ $(CXXLIBS) $(CXXINCLUDES)

.PHONY: run clean
run:
	mpirun -np 4 ./fem -d 3 -o FIRST -ksp_monitor

clean:
	rm -rf fem
