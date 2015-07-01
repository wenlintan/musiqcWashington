
#ifndef INPUT__H
#define INPUT__H

#pragma once

#include "stdafx.h"

enum KB_INPUT { 
	K_NO_INPUT,
	K_A = 'A', K_B, K_C, K_D, K_E, K_F, K_G, K_H, K_I, K_J, K_K, K_L, K_M, 
	K_N,       K_O, K_P, K_Q, K_R, K_S, K_T, K_U, K_V, K_W, K_X, K_Y, K_Z,
	K_0 = '0', K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9,
	K_LEFT, K_UP, K_RIGHT, K_DOWN,  
	K_NKEYS
};

class InputController {
public:
	// non_blocking check for keyboard input
	virtual KB_INPUT keys_pressed() = 0;
};

#if defined(WINDOWS) || defined(WIN32)
class WindowsInputController: public InputController {
public:
	WindowsInputController();
	~WindowsInputController();

	virtual KB_INPUT keys_pressed();

private:
	size_t			nread, last_processed;
};

#elif defined(LINUX)
class LinuxInputController: public InputController {
public:
	LinuxInputController();
	~LinuxInputController();

	virtual KB_INPUT keys_pressed();
};

#endif
#endif
