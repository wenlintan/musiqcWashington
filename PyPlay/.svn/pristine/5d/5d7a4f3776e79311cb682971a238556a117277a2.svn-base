
#include <cstring>

#include <algorithm>
#include <string>

//read from custom read line function in raw mode if necessary
char* read_line();
struct TTYFlexLexer: public yyFlexLexer {
	TTYFlexLexer( const std::string& data ): source_set( true ), source( data )
	{}

	TTYFlexLexer(): source_set( false )
	{}

	int yylex();

protected:
	virtual int LexerInput( char* buf, int max_size ) {
		static bool is_tty = isatty(0);
		if( !is_tty && !source_set )	return yyFlexLexer::LexerInput( buf, max_size );

		if( !source_set && !source.length() )		source = read_line();
		if( !source.length() )						return 0;

		int cpy = std::min( source.length(), (size_t)(max_size-1) );
		strncpy( buf, source.c_str(), cpy );
		source = source.substr( cpy );
		return cpy;
	}

	bool 			source_set;
	std::string 	source;
};
