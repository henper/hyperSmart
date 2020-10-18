
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

def gridFactory(config, width, height, actionLibrary):
    divx, divy = tuple(config['divs'])
    grid = Grid(divx, divy, (width, height))

    # handle any merges
    try:
        for merge in config['merges']:
            coords = [tuple(l) for l in merge]
            grid.mergeElements(coords)
    except KeyError:
        if err.args[0] == 'merges':
            pass
        else:
            raise
    
    # set all specified elements, must specify at least one
    for element in config['elements']:
        pos = tuple(element['pos'])
        
        # FIXME: figure out some proper error handling :( this includes the element callback kwargs
        #optionalKeys = ['icon', 'slider', 'text', 'touch', 'touchArgs', 'release', 'releaseArgs']

        # Decide on element type #FIXME: has to be done before setting other attributes as the original element will be destroyed upon setting type
        try:
            grid.setIcon(pos, element['icon'])
        except KeyError as err:
            if err.args[0] == 'icon':
                pass
            else:
                raise

        try:
            grid.setSlider(pos, element['slider'])
        except KeyError as err:
            if err.args[0] == 'slider':
                pass
            else:
                raise

        try:
            grid.setTextBox(pos, element['text'])
        except KeyError as err:
            if err.args[0] == 'text':
                pass
            else:
                raise

        x,y = pos
        try:
            grid.elem[x][y].setTouchAction(actionLibrary[element['touch']], **element['touchArgs'])
        except KeyError as err:
            if err.args[0] == 'touch' or err.args[0] == 'touchArgs':
                pass
            else:
                raise

        try:
            grid.elem[x][y].setReleaseAction(actionLibrary[element['release']], **element['releaseArgs'])
        except KeyError as err:
            if err.args[0] == 'release' or err.args[0] == 'releaseArgs':
                pass
            else:
                raise

    return grid

class Grid(Element):
    def __init__(self, divx, divy, size, pos = (0,0)):
        super().__init__(pos, size)

        x, y = pos
        width, height = size   

        # make sure it's all nice and neat, no errant pixels
        checkEvenDivisor(width,  divx)
        checkEvenDivisor(height, divy)

        # determine each element size
        xlen = int(width  / divx)
        ylen = int(height / divy)
        size = (xlen, ylen)

        # Create origin (top left corner) of each element
        self.elem = [] # store in grid positions
        for rowIndex in range(divy):
            row = []
            for colIndex in range(divx):
                topleft = (x + colIndex * xlen, y + rowIndex * ylen)
                row.append(Element(topleft, size))
                e = row.copy()
            row.clear()
            self.elem.append(e)
        
        # flatten grid to a single list for easier iteration
        self.elems = []
        self.elems = [item for sublist in self.elem for item in sublist]
    
    def draw(self, canvas):
        for elem in self.elems:
            elem.draw(canvas)

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

                # account for inception
                try:
                    elem, yrate = elem.getElement(click)
                except:
                    pass
                
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

    def setGrid(self, coord, divx, divy):
        # get a hold of the element we're going to destroy
        x, y = coord
        deprecated = self.elem[x][y]

        # extract the important bits
        position = deprecated.rect.topleft
        size = deprecated.rect.size

        # create a Grid-within-grid and with that, a brand spanking new element
        grid = Grid(divx, divy, size, position)

        # replace the references of the old element in the grid with the new
        self.setElement(coord, grid)