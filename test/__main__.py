import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname('__file__'), 'friends')))

loader = unittest.TestLoader()
testSuite = loader.discover('test')
testRunner = unittest.TextTestRunner(verbosity=2)
testRunner.run(testSuite)
