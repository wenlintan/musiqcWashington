
#include "shader.h"

bool Shader::initialize( const string& filename ) {

	ifstream file( filename.c_str() );
	if(!file.is_open())  
		return false;

	file.seekg( 0, ios::end );
	long fileSize = file.tellg();		//get length of file
	file.seekg( 0, ios::beg );

	char* data = new char[fileSize];
	for( long i = 0; i < fileSize; ++i )	data[i] = '\0';
	file.read(data, fileSize);
	Source = data;

	file.close();
	delete [] data;

	return true;
}

void Shader::shutdown() {

}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Program 

bool Program::initialize( shared_ptr<Shader> vert, shared_ptr<Shader> frag ) {
	Vertex	= vert;
	Frag	= frag;
	return true;
}

void Program::shutdown() {

}
