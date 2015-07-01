
CC = g++ -O3 -I/usr/include/mpi
LIBS = -lcfitsio -lgsl -lgslcblas -lhdf5 -lmpi -lmpi++

analyze: main.cpp load_gtri.o fem_data.o
	$(CC) -o $@ $^ $(LIBS)

fem_data.o: fem_data.cpp fem_data.hpp
	$(CC) -o $@ -c -g fem_data.cpp

load_gtri.o: load_gtri.cpp load_gtri.hpp fem_data.hpp
	$(CC) -o $@ -c -g load_gtri.cpp

clean:
	rm -rf analyze fem_data.o load_gtri.o


