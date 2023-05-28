import unittest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from grid import Grid, gridFactory

class Test(unittest.TestCase):
    def testCreateConfig(self):

        # simplest possible case
        factoryConfig = {'divs':   [1,1],
                         'merges': [],
                         'elements': [{'pos': [0,0]}]}
        grid = gridFactory(factoryConfig, 100, 100, None)
        config = grid.createConfig()
        assert(factoryConfig == config)

        # simple case
        factoryConfig = {'divs':   [2,1],
                         'merges': [],
                         'elements': [{'pos': [0,0]},
                                      {'pos': [1,0]}]}
        grid = gridFactory(factoryConfig, 100, 100, None)
        config = grid.createConfig()
        assert(factoryConfig == config)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main(exit=False)