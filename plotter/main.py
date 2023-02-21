from py5 import Sketch

class TestSketch(Sketch):

    def settings(self):
        self.size(300, 200)

    def setup(self):
        self.rect_mode(self.CENTER)

    def draw(self):
        self.rect(self.mouse_x, self.mouse_y, 10, 10)


test = TestSketch()
test.run_sketch()
