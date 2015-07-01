
#include <iomanip>
#include <cstdlib>
#include <windows.h>

#include "renderer.h"

void WindowsTextRenderer::clear_screen() {
	COORD coordScreen = { 0, 0 };
	DWORD cCharsWritten;

	DWORD dwConSize;
	CONSOLE_SCREEN_BUFFER_INFO csbi;
	HANDLE hConsole = GetStdHandle( STD_OUTPUT_HANDLE );

	GetConsoleScreenBufferInfo( hConsole, &csbi );
	dwConSize = csbi.dwSize.X * csbi.dwSize.Y;

	FillConsoleOutputCharacter( hConsole, TEXT(' '), dwConSize, coordScreen, &cCharsWritten );
	GetConsoleScreenBufferInfo( hConsole, &csbi );

	FillConsoleOutputAttribute( hConsole, csbi.wAttributes, dwConSize, coordScreen, &cCharsWritten);
	SetConsoleCursorPosition( hConsole, coordScreen );
}

void WindowsTextRenderer::show_cursor( bool vis ) {
	CONSOLE_CURSOR_INFO info;
	info.dwSize = 3;		info.bVisible = (BOOL)vis;

	HANDLE hConsole = GetStdHandle( STD_OUTPUT_HANDLE );
	SetConsoleCursorInfo( hConsole, &info );
}

void WindowsTextRenderer::put_cursor( ushort x, ushort y ) {
	COORD point;
	point.X = x; point.Y = y;
	SetConsoleCursorPosition( GetStdHandle(STD_OUTPUT_HANDLE), point );
}

void WindowsTextRenderer::put_glyph( const Glyph& g, ushort x, ushort y ) {
	COORD point;
	point.X = x; point.Y = y;
	SetConsoleCursorPosition( GetStdHandle(STD_OUTPUT_HANDLE), point );

	WORD flags = 0;
	switch( g.bg_color ) {
		case BLACK:				flags |= 0;						break;
		case RED:				flags |= BACKGROUND_RED;		break;
		case GREEN:				flags |= BACKGROUND_GREEN;		break;
		case BLUE:				flags |= BACKGROUND_BLUE;		break;
		case MAGENTA:			flags |= BACKGROUND_RED | BACKGROUND_BLUE;		break;
		case CYAN:				flags |= BACKGROUND_GREEN | BACKGROUND_BLUE;	break;
		case YELLOW: 			flags |= BACKGROUND_RED | BACKGROUND_GREEN;		break;
		case GRAY:				flags |= BACKGROUND_INTENSITY;					break;
		case BRIGHT_RED:		flags |= BACKGROUND_INTENSITY | BACKGROUND_RED;			break;
		case BRIGHT_GREEN:		flags |= BACKGROUND_INTENSITY | BACKGROUND_GREEN;		break;
		case BRIGHT_BLUE: 		flags |= BACKGROUND_INTENSITY | BACKGROUND_BLUE;		break;
		case BRIGHT_MAGENTA:	flags |= BACKGROUND_INTENSITY | BACKGROUND_RED | BACKGROUND_BLUE;		break;
		case BRIGHT_CYAN:		flags |= BACKGROUND_INTENSITY | BACKGROUND_GREEN | BACKGROUND_BLUE;		break;
		case BRIGHT_YELLOW:		flags |= BACKGROUND_INTENSITY | BACKGROUND_RED | BACKGROUND_GREEN;		break;
		case WHITE:				flags |= BACKGROUND_INTENSITY | BACKGROUND_RED | BACKGROUND_GREEN | BACKGROUND_BLUE;		break;
	}

	switch( g.fg_color ) {
		case BLACK:				flags |= 0;						break;
		case RED:				flags |= FOREGROUND_RED;		break;
		case GREEN:				flags |= FOREGROUND_GREEN;		break;
		case BLUE:				flags |= FOREGROUND_BLUE;		break;
		case MAGENTA:			flags |= FOREGROUND_RED | FOREGROUND_BLUE;		break;
		case CYAN:				flags |= FOREGROUND_GREEN | FOREGROUND_BLUE;	break;
		case YELLOW: 			flags |= FOREGROUND_RED | FOREGROUND_GREEN;		break;
		case GRAY:				flags |= FOREGROUND_INTENSITY;					break;
		case BRIGHT_RED:		flags |= FOREGROUND_INTENSITY | FOREGROUND_RED;			break;
		case BRIGHT_GREEN:		flags |= FOREGROUND_INTENSITY | FOREGROUND_GREEN;		break;
		case BRIGHT_BLUE: 		flags |= FOREGROUND_INTENSITY | FOREGROUND_BLUE;		break;
		case BRIGHT_MAGENTA:	flags |= FOREGROUND_INTENSITY | FOREGROUND_RED | FOREGROUND_BLUE;		break;
		case BRIGHT_CYAN:		flags |= FOREGROUND_INTENSITY | FOREGROUND_GREEN | FOREGROUND_BLUE;		break;
		case BRIGHT_YELLOW:		flags |= FOREGROUND_INTENSITY | FOREGROUND_RED | FOREGROUND_GREEN;		break;
		case WHITE:				flags |= FOREGROUND_INTENSITY | FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE;		break;
	}

	SetConsoleTextAttribute( GetStdHandle(STD_OUTPUT_HANDLE), flags );
	cout << g.symbol;
}

void WindowsTextRenderer::put_string( const string& s, ushort x, ushort y ) {

}