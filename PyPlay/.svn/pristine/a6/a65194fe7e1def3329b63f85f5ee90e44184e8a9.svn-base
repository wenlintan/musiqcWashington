
CXX = g++
CXXFLAGS = -O0

SRCDIR = .

.PHONY: all
all: bin/raytracer

tmp/collision.o: collision.cpp collision.h math.h
	$(CXX) -o $@ -c $(CXXFLAGS) collision.cpp

tmp/material.o: material.cpp material.h scene.h collision.h objects.h math.h
	$(CXX) -o $@ -c $(CXXFLAGS) material.cpp

tmp/objects.o: objects.cpp objects.h collision.h math.h
	$(CXX) -o $@ -c $(CXXFLAGS) objects.cpp

tmp/scene.o: scene.cpp scene.h collision.h objects.h math.h
	$(CXX) -o $@ -c $(CXXFLAGS) scene.cpp

bin/raytracer: raytracer.cpp tmp/collision.o tmp/material.o tmp/objects.o tmp/scene.o
	$(CXX) -o $@ $(LDFLAGS) raytracer.cpp tmp/collision.o tmp/material.o tmp/objects.o tmp/scene.o

.PHONY: clean
clean:
	rm -rf tmp/* *~ bin/raytracer
