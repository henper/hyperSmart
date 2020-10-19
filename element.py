'''
Storage container for a grapical element in the grid
'''
from pygame import Rect, image, Surface, ftfont
from pygame import SRCALPHA, BLEND_RGBA_MULT
from svg import Parser, Rasterizer # pynanosvg, depends on Cython

rasterizer = Rasterizer()

BLACK = (0,0,0,0)
TEAL = (20, 217, 210)

# Helper function to put a transparancy filter on top of any surface, alpha between 0 and 1.0
def setSurfaceOpacity(surf, alpha):
    if alpha >= 1.0:
        return

    alphaLaval = int(alpha*255)
    #self.surf.set_alpha(alphaLaval) TODO: this might be enough on pygame 2.0 but prev. releases do not support combining per-surface and per-pixel alphas
    surf.convert_alpha()
    overlay = Surface(surf.get_rect().size, SRCALPHA)
    overlay.fill((255,255,255,alphaLaval))
    surf.blit(overlay, (0,0), special_flags=BLEND_RGBA_MULT)

# Base class for individual grid elements
class Element:
    def __init__(self, pos, size):
        self.rect = Rect(pos, size)
        self.opacity = 1.0

        self.touchCallback = None
        self.touchKwargs = None

        self.releaseCallback = None
        self.releaseKwargs = None

    def setTouchAction(self, callback, **kwargs):
        self.touchCallback = callback
        self.touchKwargs = kwargs

    def onTouch(self, **kwargs):
        if self.touchCallback is None:
            return # no callback registered
        if self.touchKwargs is not None:
            mergedKwargs = {**self.touchKwargs, **kwargs} # replace with x = y | z to merge dicts in python3.9
        else:
            mergedKwargs = kwargs
        self.touchCallback(self, **mergedKwargs)

    def setReleaseAction(self, callback, **kwargs):
        self.releaseCallback = callback
        self.releaseKwargs = kwargs

    def onRelease(self, **kwargs):
        if self.releaseCallback is None:
            return # no callback registered
        if self.releaseKwargs is not None:
            mergedKwargs = {**self.releaseKwargs, **kwargs} # replace with x = y | z to merge dicts in python3.9
        else:
            mergedKwargs = kwargs
        self.releaseCallback(self, **mergedKwargs)

    def highlight(self):
        self.opacity = 1.0

    def mute(self):
        self.opacity = 0.5

    def draw(self, canvas):
        try:
            if self.opacity < 1.0:
                surf = self.surf.copy() # apply opacity filter on a copy of the surface so that subsequent draws do not mute into oblivion
                setSurfaceOpacity(surf, self.opacity)
            else:
                surf = self.surf

            canvas.fill(BLACK, rect=self.rect) # blank area
            canvas.blit(surf, self.rect.topleft)
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
        super().onTouch()
        # draw after the super call to allow further modification of the surface
        self.draw(kwargs['canvas'])

    def onRelease(self, **kwargs):
        # change the icon state to show the pressed (scaled down) version
        self.surf = self.surfDefault
        super().onRelease()
        # draw after the super call to allow further modification of the surface
        self.draw(kwargs['canvas'])

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

        try:
            super().onTouch(**kwargs)
        except AttributeError:
            pass # no on touch callback defined for element

class TextBox(Element):
    def __init__(self, pos, size, text):
        super().__init__(pos, size)

        aa = True
        fg = TEAL
        bg = BLACK
        
        ftfont.init() # perhaps not spectacular to init the font system here but should be safe to do again and again
        abel = ftfont.Font('fonts/abel/Abel-Regular.ttf', int(self.rect.height*0.75))
        self.surf = abel.render(text, aa, fg, bg)
