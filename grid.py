
'''
Class to create and store a grid pattern of generic dimensions

    Store references to display elements and their positions.
    Given click event positions, determine which element should be activated.
    
'''
from element import *

def checkEvenDivisor(length, div):
    if length % div != 0:
        raise ValueError(f'{len} is divisable by almost everything but not by {div}, try again!')

class Grid:
    def __init__(self, divx, divy, width, height):
        # store properties of the display surface 
        self.width = width
        self.height = height

        # Create origin (top left corner) of each element        
        checkEvenDivisor(width,  divx)
        checkEvenDivisor(height, divy)

        self.xlen = int(width  / divx)
        self.ylen = int(height / divy)

        self.elem = [] # store in grid positions
        for rowIndex in range(divy):
            row = []
            for colIndex in range(divx):
                topleft = (colIndex * self.ylen, rowIndex * self.xlen)
                size = (self.xlen, self.xlen)
                row.append(Element(topleft, size))
                e = row.copy()
            row.clear()
            self.elem.append(e)
        
        # flatten grid to a single list for easier iteration
        self.elems = []
        self.elems = [item for sublist in self.elem for item in sublist]
    
    def getElement(self, click=(0,0)):
        for elem in self.elems:
            if elem.rect.collidepoint(click):
                yrel = elem.rect.bottom - click[1]
                yrate = float(yrel) / elem.rect.height
                return elem, yrate
        return None

    def setElement(self, x, y, element):
        # typically there is always a existing element at every grid position
        
        # replace in iterable
        deprecated = self.elem[x][y]
        index = self.elems.index(deprecated)
        self.elems.pop(index)
        self.elems.append(element)

        # replace in grid
        self.elem[x][y] = element

    def setIcon(self, x, y, svg):
        # get a hold of the element we're going to destroy
        deprecated = self.elem[x][y]

        # extract the important bits
        position = deprecated.rect.topleft
        size = deprecated.rect.size
        
        # create an icon and with that, a brand spanking new element
        icon = Icon(position, size, svg)

        # replace the references of the old element in the grid with the new
        self.setElement(x, y, icon)

    def setSlider(self, x, y, ratio):
        # get a hold of the element we're going to destroy
        deprecated = self.elem[x][y]

        # extract the important bits
        position = deprecated.rect.topleft
        size = deprecated.rect.size

        # create a slider and with that, a brand spanking new element
        slider = Slider(position, size, ratio)

        # replace the references of the old element in the grid with the new
        self.setElement(x, y, slider)

    def setTextBox(self, x, y, ratio):
        # get a hold of the element we're going to destroy
        deprecated = self.elem[x][y]

        # extract the important bits
        position = deprecated.rect.topleft
        size = deprecated.rect.size

        # create a Text-box and with that, a brand spanking new element
        tbox = TextBox(position, size, ratio)

        # replace the references of the old element in the grid with the new
        self.setElement(x, y, tbox)