import unittest

from modelo.model.model import Model
import modelo.trait.trait_types as field

class ModelUpdateTests(unittest.TestCase):
    def setUp(self):
        class Car(Model):
            number = field.Integer(1)
            color = field.String("blue")

        self.car = Car.create()

    def test_update_empty(self):
        """
        Model.update should work with empty data.
        """
        self.car.update({})
