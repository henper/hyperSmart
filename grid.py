
'''
Class to create and store a grid pattern of generic dimensions

    Store references to display elements and their positions.
    Given click event positions, determine which element should be activated.
    
'''
from element import *
from operator import sub

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
        for colIndex in range(divx):
            row = []
            #for colIndex in range(divx):
            for rowIndex in range(divy):
                topleft = (colIndex * self.ylen, rowIndex * self.xlen)
                size = (self.xlen, self.xlen)
                row.append(Element(topleft, size))
                e = row.copy()
            row.clear()
            self.elem.append(e)
        
        # flatten grid to a single list for easier iteration
        self.elems = []
        self.elems = [item for sublist in self.elem for item in sublist]

    ''' Merge _adjacent_ elements
          coords : list of tuples with the x,y positions of all elements to be merge
                   Note! First element must be the    top-left  grid position
                         Last  element must be the bottom-right grid position
    '''
    def mergeElements(self, coords):
        # grab position from the first element
        x,y = coords[0]
        pos = self.elem[x][y].rect.topleft

        # aggregate the sizes from all elements
        # (by taking the last elment position and size we can merge several x and y levels)
        x,y = coords[-1]
        last = self.elem[x][y]
        size = tuple(map(sub, last.rect.bottomright, pos)) # element-wise subtraction of tuples

        # create a new element
        merged = Element(pos, size)

        # clean up old-elements
        for coord in coords:
            x,y = coord
            # remove all old elements from flat list   
            index = self.elems.index(self.elem[x][y])
            self.elems.pop(index)

            # to keep matrix indexing intact, instead of popping elments -set them to null
            self.elem[x][y] = None

        # keep the merged element reference in matrix position of the top-left element and in the flat list
        x,y = coords[0]
        self.elem[x][y] = merged
        self.elems.append(merged)
    
    def getElement(self, click=(0,0)):
        for elem in self.elems:
            if elem.rect.collidepoint(click):
                yrel = elem.rect.bottom - click[1]
                yrate = float(yrel) / elem.rect.height
                return elem, yrate
        return None

    def setElement(self, coord, element):
        # typically there is always a existing element at every grid position
        
        # replace in iterable
        x, y = coord
        deprecated = self.elem[x][y]
        index = self.elems.index(deprecated)
        self.elems.pop(index)
        self.elems.append(element)

        # replace in grid
        self.elem[x][y] = element

    def setIcon(self, coord, svg):
        # get a hold of the element we're going to destroy
        x, y = coord
        deprecated = self.elem[x][y]

        # extract the important bits
        position = deprecated.rect.topleft
        size = deprecated.rect.size
        
        # create an icon and with that, a brand spanking new element
        icon = Icon(position, size, svg)

        # replace the references of the old element in the grid with the new
        self.setElement(coord, icon)

    def setSlider(self, coord, ratio):
        # get a hold of the element we're going to destroy
        x, y = coord
        deprecated = self.elem[x][y]

        # extract the important bits
        position = deprecated.rect.topleft
        size = deprecated.rect.size

        # create a slider and with that, a brand spanking new element
        slider = Slider(position, size, ratio)

        # replace the references of the old element in the grid with the new
        self.setElement(coord, slider)

    def setTextBox(self, coord, ratio):
        # get a hold of the element we're going to destroy
        x, y = coord
        deprecated = self.elem[x][y]

        # extract the important bits
        position = deprecated.rect.topleft
        size = deprecated.rect.size

        # create a Text-box and with that, a brand spanking new element
        tbox = TextBox(position, size, ratio)

        # replace the references of the old element in the grid with the new
        self.setElement(coord, tbox)