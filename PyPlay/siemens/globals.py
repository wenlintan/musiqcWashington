import pygame

num_reductions = 3

color_exact_match_epsilon = 2
color_close_epsilon = 8

open_list_max_distance = 10
locked_list_max_size = 50
min_end_start_termination = 6

screen = None   # should be used strictly for debug drawing
debug_simplified = True


if pygame.font.get_init():
    font_size = 12
    font_name = pygame.font.get_default_font()
    font = pygame.font.Font(font_name, font_size)

    font_available = True

else:
    print "Warning no fonts: sdl_ttf is probably not available"
    font_available = False


def exact_color_match(color, color2):
    diff = abs(color[0] - color2[0])
    diff += abs(color[1] - color2[1])
    diff += abs(color[2] - color2[2])
    if diff > color_exact_match_epsilon:
        return False

    return True

def close_color_match(color, color2):
    diff = abs(color[0] - color2[0])
    diff += abs(color[1] - color2[1])
    diff += abs(color[2] - color2[2])
    if diff > color_close_epsilon:
        return False
    
    return True
    
