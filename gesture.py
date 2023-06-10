
from pygame import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, FINGERDOWN, FINGERUP, FINGERMOTION, QUIT, KEYDOWN, K_c, key, KMOD_CTRL
from enum import Enum

WIDTH = 720
HEIGHT = 720

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
    pdx = 0.0

    event = Gesture.NONE
    __down_position = (0,0)

    def get_supported_events(self):
        return [MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, FINGERDOWN, FINGERUP, FINGERMOTION, QUIT, KEYDOWN]

    def update(self, event) -> Gesture:

        # Allow for ways to exit the application
        if event.type == QUIT or event.type == KEYDOWN and event.key == K_c and key.get_mods() & KMOD_CTRL:
            self.event = Gesture.QUIT
            return Gesture.QUIT

        if hasattr(event, 'x') :  # finger events has x,y,dx,dy
            self.position = int((WIDTH-1) * (1.0 - event.x)), int((HEIGHT-1) * (1.0 - event.y))
            #self.velocity = int(WIDTH * (self.pdx - event.dx))
            self.pdx = event.dx
        elif hasattr(event, 'pos') : # mouse event
            #self.velocity = self.position[0] - event.pos[0]
            self.position = event.pos

        #print(f' event type: {event.type} position x: {self.position[0]} y: {self.position[1]}, dx: {getattr(event, "dx", "-")} dy: {getattr(event, "dy", "-")}')

        if (event.type in [MOUSEBUTTONDOWN, FINGERDOWN]):
            self.__down_position = self.position
            self.event = Gesture.DOWN

        elif (event.type == FINGERMOTION or event.type == MOUSEMOTION and event.buttons[0] == 1):
            self.velocity = 1 if self.travel > 0 else -1
            if hasattr(event, 'dx') :
                self.travel = int(event.dx * WIDTH)
            else:
                self.travel = self.__down_position[0] - self.position[0]

            if abs(self.travel) > 20:
                self.event = Gesture.SWIPE


        elif (event.type in [MOUSEBUTTONUP, FINGERUP]):
            if (self.event != Gesture.SWIPE):
                self.event = Gesture.UP
            else:
                self.event = Gesture.NONE
                return Gesture.SWUP

        return self.event
