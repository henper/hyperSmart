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
        buf = rasterizer.rasterize(svg, width, height, scale * 0.9) # TODO: add tx, ty for offset
        self.surfPressed = image.frombuffer(buf, self.rect.size, 'RGBA')

    def setSurface(self, surf):
        self.surf = surf
    def setSurfacePressed(self, surf):
        self.surfPressed = surf
    def setSurfaces(self, surfs):
        self.surf = surfs[0]
        self.surfPressed = surfs[1]