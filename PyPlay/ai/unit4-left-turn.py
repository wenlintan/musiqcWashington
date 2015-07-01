# ----------
# User Instructions:
# 
# Implement the function optimum_policy2D() below.
#
# You are given a car in a grid with initial state
# init = [x-position, y-position, orientation]
# where x/y-position is its position in a given
# grid and orientation is 0-3 corresponding to 'up',
# 'left', 'down' or 'right'.
#
# Your task is to compute and return the car's optimal
# path to the position specified in `goal'; where
# the costs for each motion are as defined in `cost'.

# EXAMPLE INPUT:

# grid format:
#     0 = navigable space
#     1 = occupied space 
grid = [[1, 1, 1, 0, 0, 0],
        [1, 1, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 1, 1],
        [1, 1, 1, 0, 1, 1]]
goal = [2, 0] # final position
init = [4, 3, 0] # first 2 elements are coordinates, third is direction
cost = [2, 1, 10] # the cost field has 3 values: right turn, no turn, left turn

# EXAMPLE OUTPUT:
# calling optimum_policy2D() should return the array
# 
# [[' ', ' ', ' ', 'R', '#', 'R'],
#  [' ', ' ', ' ', '#', ' ', '#'],
#  ['*', '#', '#', '#', '#', 'R'],
#  [' ', ' ', ' ', '#', ' ', ' '],
#  [' ', ' ', ' ', '#', ' ', ' ']]
#
# ----------


# there are four motion directions: up/left/down/right
# increasing the index in this array corresponds to
# a left turn. Decreasing is is a right turn.

forward = [[-1,  0], # go up
           [ 0, -1], # go left
           [ 1,  0], # go down
           [ 0,  1]] # do right
forward_name = ['up', 'left', 'down', 'right']

# the cost field has 3 values: right turn, no turn, left turn
action = [-1, 0, 1]
action_name = ['R', '#', 'L']


# ----------------------------------------
# modify code below
# ----------------------------------------

def optimum_policy2D():
    policy = [[[-1 for row in range(len(grid[0]))] for col in range(len(grid))]
        for i in range(4)]
    value = [[[999 for row in range(len(grid[0]))] for col in range(len(grid))]
        for i in range(4)]
        
    for i in range(4):
        policy[i][goal[0]][goal[1]] = 0
        value[i][goal[0]][goal[1]] = 0
    
    change = True
    while change:
        change = False
        for d in range(4):
            for x in range(len(grid)):
                for y in range(len(grid[0])):
                    v = value[d][x][y]
                    
                    if grid[x][y]:
                        continue
                    for a in range(len(action)):
                    	dx, dy = forward[(d+action[a])%4]
                    	if x+dx < 0 or x+dx >= len(grid) or y+dy < 0 or y+dy >= len(grid[0]):
                        	continue
                        if value[(d+action[a])%4][x+dx][y+dy] + cost[a] < v:
                            change = True
                            v = value[d][x][y] = \
                            	value[(d+action[a])%4][x+dx][y+dy] + cost[a]
                            policy[d][x][y] = a
    print
    print
    for i in range(4):
        print "Dir", forward_name[i]
        for l in value[i]:
            print l
    
    x, y, d = init
    policy2D = [[' ' for row in range(len(grid[0]))] for col in range(len(grid))]
    policy2D[goal[0]][goal[1]] = '*'

    while [x, y] != goal:
        a = policy[d][x][y]
        policy2D[x][y] = action_name[a]
        dx, dy = forward[(d+action[a])%4]
        x, y, d = x+dx, y+dy, (d+action[a])%4
    return policy2D # Make sure your function returns the expected grid.

for l in optimum_policy2D():
	print l

