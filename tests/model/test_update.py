import unittest

from modelo.model.model import Model
import modelo.trait.trait_types as field

class ModelUpdateTests(unittest.TestCase):
    def test_update_empty(self):
        """
        Model.update should work with empty data.
        """
        model = Model()
        model.update({})
