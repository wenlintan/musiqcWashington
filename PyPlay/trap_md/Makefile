CC=g++
CC_FLAGS=-I/home/wrightj/boost_1_54_0
LINK_FLAGS=-L/home/wrightj/boost_1_54_0/stage/lib

all: sim fit

sim: main.cpp
	$(CC) $^ -o $@ $(CC_FLAGS) $(LINK_FLAGS) -lboost_thread -lboost_system

fit: fit.cpp
	$(CC) $^ -o $@ $(CC_FLAGS) $(LINK_FLAGS) -lgsl -lgslcblas

clean:
	rm -rf fit sim
