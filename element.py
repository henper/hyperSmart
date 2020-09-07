'''
Storage container for a grapical element in the grid
'''
from pygame import Rect, image, Surface, font
from svg import Parser, Rasterizer # pynanosvg, depends on Cython

rasterizer = Rasterizer()

BLACK = (0,0,0,0)
TEAL = (20, 217, 210)

# Base class for individual grid elements
class Element:
    def __init__(self, pos, size):
        self.rect = Rect(pos, size)

    def setTouchAction(self, callback):
        self.touchCallback = callback

    def onTouch(self, **kwargs):
        self.touchCallback()

    def setReleaseAction(self, callback):
        self.releaseCallback = callback

    def onRelease(self, **kwargs):
        self.releaseCallback()

    def draw(self, canvas):
        try:
            canvas.fill(BLACK, rect=self.rect) # blank area
            canvas.blit(self.surf, self.rect.topleft)
        except AttributeError:
            pass # happens when caller attempts to draw an element without setting a derived class

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
        self.surfDefault = image.frombuffer(buf, self.rect.size, 'RGBA')

        # make a mini version for activation state
        buf = rasterizer.rasterize(svg, width, height, scale * ds, tx = dx*width, ty =dy*height)
        self.surfPressed = image.frombuffer(buf, self.rect.size, 'RGBA')

        # initialize the active surface
        self.surf = self.surfDefault

    def onTouch(self, **kwargs):
        # change the icon state to show the pressed (scaled down) version
        self.surf = self.surfPressed
        self.draw(kwargs['canvas'])

        try:
            super().onTouch()
        except AttributeError:
            pass # no on touch callback defined for element

    def onRelease(self, **kwargs):
        # change the icon state to show the pressed (scaled down) version
        self.surf = self.surfDefault
        self.draw(kwargs['canvas'])

        try:
            super().onRelease()
        except AttributeError:
            pass # no on touch callback defined for element

class Slider(Element):
    def __init__(self, pos, size, ratio):
        super().__init__(pos, size)

        # use the same size for the icon as the grid element
        self.surf = Surface(self.rect.size)
        self.setSlider(ratio)

    def setSlider(self, ratio):
        ''' Create a Rectangle corresponding to the slider position
            position will be relative to the surface so modify the top acc. to ratio
        '''
        rect = Rect((0,0), self.rect.size) # set position to origin as fill rect is relative to surface
        rect.top = rect.height - int(rect.height * ratio) # change position
        rect.height = int(rect.height * ratio) # change size

        self.surf.fill(TEAL, rect=rect)

        # now fill in what's remaining with background
        brect = Rect((0,0), self.rect.size)
        brect.height = rect.top

        self.surf.fill(BLACK, rect=brect)

    def onTouch(self, **kwargs):
        self.setSlider(kwargs['yrate'])
        self.draw(kwargs['canvas'])

class TextBox(Element):
    def __init__(self, pos, size, text):
        super().__init__(pos, size)

        aa = True
        fg = TEAL
        bg = BLACK
        
        font.init() # perhaps not spectacular to init the font system here but should be safe to do again and again
        abel = font.Font('fonts/abel/Abel-Regular.ttf', int(self.rect.height*0.75))
        self.surf = abel.render(text, aa, fg, bg)
