
'''
Class to create and store a grid pattern of generic dimensions

    Store references to display elements and their positions.
    Given click event positions, determine which element should be activated.
    
'''
from element import Element

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
                return elem
        return None
