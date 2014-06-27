import unittest

from modelo.model.model import Model
import modelo.trait.trait_types as field

class BasicModelTests(unittest.TestCase):
    def test_instantiation(self):
        """
        Model.__init__ should work (no params).
        """
        model = Model()
        self.assertIsInstance(model, Model)

    def test_to_dict(self):
        """
        Model.to_dict should create a dictionary.
        """
        model = Model()
        result = model.to_dict()

        # to_dict should return a dictionary
        self.assertTrue(isinstance(result, dict))

        # and it should be empty by default
        self.assertEqual(result, {})

    def test_create_no_params(self):
        """
        Model.create should work when given no params.
        """
        model = Model.create()
        self.assertTrue(isinstance(model, Model))

    def test_create_empty_dict_param(self):
        """
        Model.create should work when given an empty dictionary.
        """
        model = Model.create({})
        self.assertTrue(isinstance(model, Model))
