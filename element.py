'''
Storage container for a grapical element in the grid
'''
from pygame import Rect, image, Surface
from svg import Parser, Rasterizer # pynanosvg, depends on Cython

rasterizer = Rasterizer()

BLACK = (0,0,0,0)
TEAL = (20, 217, 210)

class Element:
    def __init__(self, pos, size):
        self.rect = Rect(pos, size)
        self.isSlider = False

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

    def setSlider(self, ratio):
        self.isSlider = True
        try:
            self.surf
        except AttributeError:
            self.surf = Surface(self.rect.size)
        
        ''' Create a Rectangle corresponding to the slider position
            position will be relative to the surface so modify the top acc. to ratio
        '''
        rect = Rect((0,0), self.rect.size) # set position to origin as fill rect is relative to surface
        rect.top = rect.height - int(rect.height * ratio)

        self.surf.fill(TEAL, rect=rect)
        self.surf.fill(BLACK, rect=Rect((0,0), (self.rect.width, self.rect.height * ratio)))

    def setAction(self, callback):
        self.callback = callback

    def setTouchAction(self, callback):
        self.onTouch = callback

    def setReleaseAction(self, callback):
        self.onRelease = callback

    def draw(self, canvas, pressed=False, yrate=0.0):
        try:
            canvas.fill(BLACK, rect=self.rect) # blank area

            if self.isSlider :
                self.setSlider(yrate)
                pressed = False

            if pressed :
                canvas.blit(self.surfPressed, self.rect.topleft)
            else:
                canvas.blit(self.surf, self.rect.topleft)
            
        except AttributeError:
            pass # happens when caller attempts to draw an element without setting graphics
             

class Icon(Element):
    def __init__(self, pos, size, svgFile):
        super().__init__(pos, size)

        # use the same size for the icon as the grid element
        width, height = self.rect.size

        # pressed version scale
        ds = 0.9
        dx = dy = (1 - ds) / 2 # the position offset to use in x and y directions

        # use pynanosvg to convert svg file to bytes
        svg = Parser.parse_file(svgFile)#, PPI) ..I do not understand DPI

        # figure out the scaling, making sure not to draw outside the lines
        scale = min(width / svg.width, height / svg.height)
        buf = rasterizer.rasterize(svg, width, height, scale)
        self.surf = image.frombuffer(buf, self.rect.size, 'RGBA')

        # make a mini version for activation state
        buf = rasterizer.rasterize(svg, width, height, scale * ds, tx = dx*width, ty =dy*height)
        self.surfPressed = image.frombuffer(buf, self.rect.size, 'RGBA')
