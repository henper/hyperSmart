
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
    velocity = 0
    travel = 0
    
    event = Gesture.NONE
    __down_position = (0,0)

    def get_supported_events(self):
        return [MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, FINGERDOWN, FINGERUP, FINGERMOTION, QUIT, KEYDOWN]

    def update(self, event) -> Gesture:

        # Allow for ways to exit the application
        if event.type == QUIT or event.type == KEYDOWN and event.key == K_c and key.get_mods() & KMOD_CTRL:
            self.event = Gesture.QUIT
            return Gesture.QUIT
        
        new_pos = getattr(event, 'pos', (0,0)) # not all events has a position attribute
        self.velocity = self.position[0] - new_pos[0]
        self.position = new_pos

        print(f' event type: {event.type} position x: {self.position[0]} y: {self.position[1]}')

        if (event.type in [MOUSEBUTTONDOWN, FINGERDOWN]):
            self.__down_position = self.position
            self.event = Gesture.DOWN

        elif (event.type == FINGERMOTION or event.type == MOUSEMOTION and event.buttons[0] == 1):
            self.travel = self.__down_position[0] - self.position[0]
            if abs(self.travel) > 20:
                self.event = Gesture.SWIPE
                

        elif (event.type in [MOUSEBUTTONUP, FINGERUP]):
            if (self.event != Gesture.SWIPE):
                self.event = Gesture.UP
            else:
                self.event = Gesture.NONE
                
                if self.travel > 1 :
                    self.velocity = 1
                else :
                    self.velocity = -1

                return Gesture.SWUP
        
        return self.event
