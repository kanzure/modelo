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
            mapping = field.Dict()

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

    def test_update_list_integers(self):
        self.car.numbers = range(5)

        self.car.update({
            "numbers": range(6),
        })

        self.assertNotEqual(self.car.numbers, range(5))
        self.assertEqual(self.car.numbers, range(6))

    def test_update_list_strings(self):
        original_value = ["red", "green", "blue"]
        new_value = ["r", "g", "b"]

        self.car.names = original_value

        self.car.update({
            "names": new_value,
        })

        self.assertEqual(self.car.names, new_value)

    def test_update_list_models(self):
        original_value = []
        new_value = [Model.create()]

        self.car.wheels = original_value

        self.car.update({
            "wheels": new_value,
        })

        self.assertEqual(self.car.wheels, new_value)

    def test_update_dict_keys_are_different(self):
        self.car.mapping = {
            "hello": "world",
        }

        original_keys = self.car.mapping.keys()

        self.car.update({
            "mapping": {
                "future": "world",
            },
        })

        self.assertNotEqual(original_keys, self.car.mapping.keys())
