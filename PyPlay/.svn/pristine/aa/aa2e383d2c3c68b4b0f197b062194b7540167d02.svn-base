
#include "input.h"

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
 
KB_INPUT map_virtual_key_code( WORD i ) {
	if( i >= 'A' && i <= 'Z' )			return (KB_INPUT)( K_A + ( i - 'A' ) );
	if( i >= '1' && i <= '9' )			return (KB_INPUT)( K_1 + ( i - '1' ) );
	if( i >= VK_LEFT && i <= VK_DOWN )	return (KB_INPUT)( K_LEFT + ( i - VK_LEFT ) );
	return K_NO_INPUT;
}

WindowsInputController::WindowsInputController() { 
    HANDLE hStdin; 
    DWORD fdwMode, fdwSaveOldMode; 
 
    // Get the standard input handle. 
    hStdin = GetStdHandle( STD_INPUT_HANDLE ); 
    if( hStdin == INVALID_HANDLE_VALUE ) 
        return;
 
    // Save the current input mode, to be restored on exit. 
    if( !GetConsoleMode(hStdin, &fdwSaveOldMode) ) 
        return; 
 
    // Enable the window and mouse input events. 
    fdwMode = ENABLE_WINDOW_INPUT | ENABLE_MOUSE_INPUT; 
    if( !SetConsoleMode(hStdin, fdwMode) ) 
        return; 
 
}

WindowsInputController::~WindowsInputController() {

}

KB_INPUT WindowsInputController::keys_pressed() {

	HANDLE hStdin = GetStdHandle( STD_INPUT_HANDLE ); 
    if( hStdin == INVALID_HANDLE_VALUE ) 
        return K_NO_INPUT;

	DWORD num_read, num_avail = 0;
	if( !GetNumberOfConsoleInputEvents( hStdin, &num_avail ) || !num_avail )
		return K_NO_INPUT;

	INPUT_RECORD	irInBuf[128];
	if( !ReadConsoleInput( hStdin, irInBuf, 128, &num_read ) ) // number of records read 
		return K_NO_INPUT; 

	for( DWORD i = 0; i < num_read; i++ ) 
	{
		switch(irInBuf[i].EventType) 
		{ 
			case KEY_EVENT: 
			{
				KEY_EVENT_RECORD rec = irInBuf[i].Event.KeyEvent;
		        if( rec.bKeyDown && map_virtual_key_code( rec.wVirtualKeyCode ) != K_NO_INPUT )
					return map_virtual_key_code( rec.wVirtualKeyCode );

		        break; 
			}

			case MOUSE_EVENT:				break; 
			case WINDOW_BUFFER_SIZE_EVENT:	break; 
			case FOCUS_EVENT:				break;
			case MENU_EVENT:				break; 

			default: 
				return K_NO_INPUT;
				break; 
		}
    } 

	return K_NO_INPUT;
}

