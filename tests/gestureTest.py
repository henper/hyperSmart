import unittest
import sys, os
from pygame import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, FINGERDOWN, FINGERUP, FINGERMOTION

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from gesture import *

class event:
    def __init__(self,t, p):
        self.type = t
        self.pos = p


class Test(unittest.TestCase):
    def testDown(self):
        gd = GestureDetection()
    
        gesture = gd.update(event(FINGERDOWN, (0,0)))
    
        assert(gesture == Gesture.DOWN)

    def testUp(self):
        gd = GestureDetection()
    
        gesture = gd.update(event(FINGERDOWN, (0,0)))
        gesture = gd.update(event(FINGERUP,   (0,0)))
    
        assert(gesture == Gesture.UP)

    def testSwipeRight(self):
        gd = GestureDetection()

        gesture = gd.update(event(FINGERDOWN,   ( 0,0)))
        gesture = gd.update(event(FINGERMOTION, (10,0)))
        gesture = gd.update(event(FINGERMOTION, (20,0)))
        gesture = gd.update(event(FINGERMOTION, (30,0)))

        assert(gesture == Gesture.SWIPE)
        assert(gd.travel == -30)

        gesture = gd.update(event(FINGERUP,     (40,0)))

        assert(gesture == Gesture.SWUP)

    def testNoPos(self):
        gd = GestureDetection()

        class positionless_event():
            type = 0
        
        gesture = gd.update(positionless_event())
        assert(gesture == Gesture.NONE)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main(exit=False)
    