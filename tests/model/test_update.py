import unittest

from modelo.model.model import Model
import modelo.trait.trait_types as field

class ModelUpdateTests(unittest.TestCase):
    def setUp(self):
        class Car(Model):
            number = field.Integer()
            color = field.String()

        self.car = Car.create({
            "number": 1,
            "color": "blue",
        })

    def test_update_empty(self):
        """
        Model.update should work with empty data.
        """
        self.car.update({})

    def test_update_integer(self):
        """
        Model.update should update some integer trait.
        """
        original_value = self.car.number
        new_value = original_value + 1

        # perform the actual update
        self.car.update({
            "number": new_value,
        })

        self.assertEqual(self.car.number, new_value)
