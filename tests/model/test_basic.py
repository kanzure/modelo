import unittest

from modelo.model.model import Model

class BasicModelTests(unittest.TestCase):
    def test_instantiation(self):
        model = Model()
        self.assertIsInstance(model, Model)
