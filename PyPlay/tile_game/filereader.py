import graphic

class File:
    def __init__(self, filename):
        self.filename = filename
        self.file = file(filename, "r")
        self.engine = graphic.Graphics()

        for line in self.file:
            print line
            if line.strip() == "<map>":
                self.read_map()
            elif line.strip() == "<images>":
                self.read_images()

        self.file.close()

    def get_graphics(self):
        return self.engine

    def read_images(self):

        for line in self.file:
            if line.strip() == "</images>":
                break
            
            data = line.split('=')
            char = data[0].strip()
            data = data[1].strip()
            
            data = data.split(' ')

            name = data[0]

            pos = [0,0]
            pos[0] = int(data[1])
            pos[1] = int(data[2])

            level = int(data[3])
            options = data[4]
                
            self.engine.create_tile(char, name, pos, level, options)

    def read_map(self):        
        sizex = self.file.next()
        sizey = self.file.next()
        
        sizex = int(sizex.strip())
        sizey = int(sizey.strip())

        worlddata = []

        for y in range(sizey):
            worlddata.append(self.file.next().split(' '))

        endworld = self.file.next()
        self.engine.create_world(worlddata)

        
            
