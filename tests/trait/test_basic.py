import unittest

from modelo.trait.trait_type import TraitType

class BasicTraitTypeTests(unittest.TestCase):
    def test_instantiation(self):
        trait_type = TraitType()
        self.assertIsInstance(trait_type, TraitType)
