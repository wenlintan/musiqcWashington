
include Makefile.host
CXX = g++
CXXFLAGS = -g $(INCLUDE) $(LIBRARY) -DLINUX

sources = action.cpp character.cpp controller.cpp entity.cpp \
	linux_input.cpp linux_renderer.cpp map.cpp renderer.cpp scripts.cpp stdafx.cpp tile.cpp \
	trigger.cpp

objects = $(patsubst %.cpp,%.o, $(sources))

.PHONY: all
all: hack

hack: hack.cpp $(objects)
	$(CXX) $(CXXFLAGS) -o $@ hack.cpp $(objects) -lpython2.6 -lboost_python-gcc43-mt-1_39

$(objects): stdafx.h
map.o: action.h
scripts.o: map.h scripts.h
map.o linux_renderer.o: map.h tile.h
linux_renderer.o: renderer.h
linux_input.o: input.h

character.o: entity.h inventory.h trigger.h

.PHONY: clean
clean:
	rm -rf *.o *~ hack $(objects)

