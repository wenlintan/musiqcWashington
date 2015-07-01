class Smooth:

    def __init__(self, array):
        self.array = array
        self.build_array()

    def build_array(self):

        width, height = len(self.array), len(self.array[0])
        for i in range(globals.num_reductions):
            for x in range( 1, width -1 ):
                for y in range(1, height -1 ):
                    c1 = self.array[x][y-1]
                    c2 = self.array[x-1][y]
                    c3 = self.array[x+1][y]
                    c4 = self.array[x][y+1]

                    r = c1[0] + c2[0] + c3[0] +c4[0]
                    g = c1[1] + c2[1] + c3[1] +c4[1]
                    b = c1[2] + c2[2] + c3[2] +c4[2]
                        
                    self.array[x][y] = [ r/4.0, g/4.0, b/4.0 ]
