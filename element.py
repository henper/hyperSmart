'''
Storage container for a grapical element in the grid
'''
from pygame import Rect, image
from svg import Parser, Rasterizer # pynanosvg, depends on Cython

rasterizer = Rasterizer()

class Element:
    def __init__(self, pos, size):
        self.rect = Rect(pos, size)

    def setGraphics(self, svgFile):
        width, height = self.rect.size

        # use pynanosvg to convert svg file to bytes
        svg = Parser.parse_file(svgFile)#, PPI) ..I do not understand DPI

        # figure out the scaling, making sure not to draw outside the lines
        scale = min(width / svg.width, height / svg.height)
        buf = rasterizer.rasterize(svg, width, height, scale)
        self.surf = image.frombuffer(buf, self.rect.size, 'RGBA')

        # make a mini version for activation state
        buf = rasterizer.rasterize(svg, width, height, scale * 0.9, tx = 0.05*width, ty =0.05*height)
        self.surfPressed = image.frombuffer(buf, self.rect.size, 'RGBA')

    def setAction(self, callback):
        self.callback = callback

    def draw(self, canvas, pressed=False):
        try:
            canvas.fill((0,0,0,0), rect=self.rect) # blank area

            if pressed :
                canvas.blit(self.surfPressed, self.rect.topleft)
            else:
                canvas.blit(self.surf, self.rect.topleft)
            
        except AttributeError:
            pass # happens when caller attempts to draw an element without setting graphics
             
