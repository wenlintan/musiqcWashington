
#include <iostream>
#include "list.hpp"

struct TestInt {
	int val;
	ListLink<TestInt> links;

	TestInt( int v ): val( v )
	{}
};

int main( int argc, char** argv ) {
	List<TestInt, &TestInt::links> test;
	test.push_back( new TestInt( 4 ) );
	test.push_back( new TestInt( 2 ) );
	test.push_back( new TestInt( 8 ) );

	std::cout << test.front().val << std::endl;
	std::cout << test.back().val << std::endl;

	delete &test.front();
	std::cout << test.front().val << std::endl;
	std::cout << test.back().val << std::endl;

	delete &test.back();
	test.push_back( new TestInt(60) );
	test.push_back( new TestInt(100) );

	List<TestInt, &TestInt::links>::iterator 
		i = test.begin(), e = test.end();
	for( ; i != e; ++i )
		std::cout << i->val << std::endl;


	return 0;
}
