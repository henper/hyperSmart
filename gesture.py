
from pygame import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, FINGERDOWN, FINGERUP, FINGERMOTION, QUIT, KEYDOWN, K_c, key, KMOD_CTRL
from enum import Enum

class Gesture(Enum):

    # Detected events and their properties
    QUIT  = -1
    NONE  =  0
    UP    =  1
    DOWN  =  2
    SWIPE =  3
    SWUP =  4

class GestureDetection():

    # states
    position = (0,0)
    travel = 0
    
    event = Gesture.NONE
    __down_position = (0,0)

    def get_supported_events():
        return [MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, FINGERDOWN, FINGERUP, FINGERMOTION, QUIT, KEYDOWN]

    def update(self, event) -> Gesture:

        # Allow for ways to exit the application
        if event.type == QUIT or event.type == KEYDOWN and event.key == K_c and key.get_mods() & KMOD_CTRL:
            self.event = Gesture.QUIT
            return Gesture.QUIT
        
        try:
            self.position = event.pos
        except AttributeError as err:
            if err.name == 'pos':
                return Gesture.NONE # not all events has a position attribute
            raise err

        if (event.type in [MOUSEBUTTONDOWN, FINGERDOWN]):
            self.__down_position = event.pos
            self.event = Gesture.DOWN

        elif (event.type == FINGERMOTION or event.type == MOUSEMOTION and event.buttons[0] == 1):
            self.travel = self.__down_position[0] - event.pos[0]
            if abs(self.travel) > 20:
                self.event = Gesture.SWIPE
                

        elif (event.type in [MOUSEBUTTONUP, FINGERUP]):
            if (self.event != Gesture.SWIPE):
                self.event = Gesture.UP
            else:
                self.event = Gesture.NONE
                return Gesture.SWUP
        
        return self.event
