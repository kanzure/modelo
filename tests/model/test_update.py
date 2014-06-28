import unittest

from modelo.model.model import Model
import modelo.trait.trait_types as field

class ModelUpdateTests(unittest.TestCase):
    def setUp(self):
        class Car(Model):
            number = field.Integer()
            color = field.String()
            things = field.List()
            numbers = field.List(field.Integer())
            names = field.List(field.String())
            wheels = field.List(field.Instance(Model))

        self.car = Car.create({
            "number": 1,
            "color": "blue",
            "things": [1, 2, "three", 4.01],
            "numbers": range(5),
            "names": ["bob", "amy", "carol"],
            "wheels": [Model.create(), Model.create()]
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

    def test_update_list_no_inner_trait(self):
        self.car.things = ["three"]

        self.car.update({
            "things": [1, 2, 3],
        })

        self.assertTrue("three" not in self.car.things)
