import unittest

from modelo.model.model import Model
import modelo.trait.trait_types as field

class BasicModelTests(unittest.TestCase):
    def test_instantiation(self):
        model = Model()
        self.assertIsInstance(model, Model)

    def test_to_dict(self):
        model = Model()
        result = model.to_dict()

        # to_dict should return a dictionary
        self.assertTrue(isinstance(result, dict))

        # and it should be empty by default
        self.assertEqual(result, {})

    def test_create_no_params(self):
        model = Model.create()
        self.assertTrue(isinstance(model, Model))

    def test_create_empty_dict(self):
        model = Model.create({})
        self.assertTrue(isinstance(model, Model))
