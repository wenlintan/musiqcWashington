

CXX = g++
CXXFLAGS = -g -fpermissive -Wall -I/home/wrightj/Desktop/Lib/boost_1_39_0

LEX = flex
YACC = bison

sources = syntax_types.cpp simplify_visitor.cpp read_line.cpp symbols.cpp
objects = syntax.tab.o lex.yy.o syntax_types.o simplify_visitor.o read_line.o symbols.o

test_sources = matrix_tests.cpp syntax_types_tests.cpp compare_visitor_tests.cpp
test_objects = matrix_tests.o syntax_types_tests.o compare_visitor_tests.o

.PHONY: all
all: calc

syntax.tab.h: syntax.y syntax_types.h lexer.h matrix.h
	$(YACC) -d syntax.y

syntax.tab.o: syntax.y syntax_types.h lexer.h matrix.h
	$(YACC) syntax.y
	$(CXX) $(CXXFLAGS) -c -o $@ syntax.tab.c

lex.yy.o: scanner.l syntax.tab.h syntax_types.h lexer.h matrix.h
	$(LEX) scanner.l
	$(CXX) $(CXXFLAGS) -c -o $@ lex.yy.cc

syntax_types.o: syntax_types.h matrix.h
simplify_visitor.o: simplify_visitor.h syntax_types.h matrix.h
symbols.o: symbols.h

calc: calc.cpp $(objects)
	$(CXX) $(CXXFLAGS) -o $@ calc.cpp $(objects) -ly -lfl

matrix_tests.o: matrix.h
syntax_types_tests.o: syntax_types.h lexer.h
compare_visitor_tests.o: syntax_types.h

test: test.cpp $(test_objects) $(objects)
	$(CXX) $(CXXFLAGS) -o $@ test.cpp $(test_objects) $(objects) -lgtest
	./test

.PHONY: clean
clean:
	rm -rf calc test syntax.tab.c syntax.tab.h lex.yy.cc *~ *.o

