
from ctypes import *
user32 = windll.user32

MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

class KeyBoardInput(Structure):
	_fields_ = [
    	("wVk", c_ushort),
		("wScan", c_ushort),
		("dwFlags", c_ulong),
		("time", c_ulong),
		("dwExtraInfo", POINTER(c_ulong))
	]

class HardwareInput(Structure):
	_fields_ = [
		("uMsg", c_ulong),
		("wParamL", c_short),
		("wParamH", c_ushort)
	]

class MouseInput(Structure):
	_fields_ = [
		("dx", c_long),
		("dy", c_long),
		("mouseData", c_ulong),
		("dwFlags", c_ulong),
		("time",c_ulong),
		("dwExtraInfo", POINTER(c_ulong))
	]

class InputUnion(Union):
	_fields_ = [
		("ki", KeyBoardInput),
		("mi", MouseInput),
		("hi", HardwareInput)
	]

class Input(Structure):
	_fields_ = [
		("type", c_ulong),
		("ii", InputUnion)
	]

class POINT(Structure):
	_fields_ = [
		("x", c_ulong),
		("y", c_ulong)
	]

mouse_click = Input * 2
extra_info = c_ulong(0)

move = InputUnion()
move.mi = MouseInput(100, 0, 0, MOUSEEVENTF_MOVE, 0, pointer(extra_info))

click = InputUnion()
click.mi = MouseInput(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, pointer(extra_info))

release = InputUnion()
release.mi = MouseInput(0, 0, 0, MOUSEEVENTF_LEFTUP, 0, pointer(extra_info))

mouse_click_input = mouse_click( (0, click), (0, release) )
mouse_move_input = Input( 0, move )

user32.SendInput( 1, pointer(mouse_move_input), sizeof(Input) )
user32.SendInput( 2, pointer(mouse_click_input), sizeof(Input) )

