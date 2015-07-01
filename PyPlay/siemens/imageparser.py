import simplified

class ImageParser:
    def __init__(self, array):
        self.array = array
        self.run()

    def run(self):
        self.first = simplified.SimplifiedPass(self.array)
        self.first_objects = self.first.get_objects()
        

    def draw_objects(self, screen):
        self.first.debug_draw_image(screen)
