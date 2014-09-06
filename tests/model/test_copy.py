from copy import (
    copy,
    deepcopy,
)

import unittest

from modelo.model.model import Model
import modelo.trait.trait_types as field

class CopyModelTests(unittest.TestCase):
    def setUp(self):
        class Limb(Model):
            extremities = field.Integer()
        self.limb_class = Limb

        class Animal(Model):
            name = field.String()
            age = field.Integer()
            legs = field.List(field.Instance(Limb))
            thing = field.Any()
        self.animal_class = Animal

        class Cage(Model):
            name = field.String()
            animal = field.Instance(Animal)
        self.cage_class = Cage

    def test_copy(self):
        limb1 = self.limb_class.create({
            "extremities": 5,
        })

        limb2 = copy(limb1)

        self.assertTrue(isinstance(limb2, limb1.__class__))
        self.assertTrue(limb2 is not limb1)
        self.assertEqual(limb1.to_dict(), limb2.to_dict())
        self.assertEqual(limb1.extremities, limb2.extremities)

    def test_copy_with_model_trait(self):
        thing = object()
        limb1 = self.limb_class.create({"extremities": 6})
        limb2 = self.limb_class.create({"extremities": 11})
        animal1 = self.animal_class.create({"name": "george", "legs": [limb1, limb2], "thing": thing})

        animal2 = copy(animal1)

        self.assertEqual(animal1.__class__, animal2.__class__)
        self.assertTrue(isinstance(animal2, animal1.__class__))
        self.assertTrue(animal2 is not animal1)
        self.assertEqual(animal1.to_dict(), animal2.to_dict())
        self.assertTrue(animal1.legs[0] is animal2.legs[0])
        self.assertTrue(animal1.legs[1] is animal2.legs[1])
        self.assertTrue(animal1.thing is animal2.thing)

    def test_deepcopy(self):
        thing = object()
        limb1 = self.limb_class.create({"extremities": 6})
        limb2 = self.limb_class.create({"extremities": 11})
        animal1 = self.animal_class.create({"name": "george", "legs": [limb1, limb2], "thing": thing})

        animal2 = deepcopy(animal1)

        self.assertEqual(animal1.__class__, animal2.__class__)
        self.assertTrue(isinstance(animal2, animal1.__class__))
        self.assertTrue(animal2 is not animal1)

        dict1 = animal1.to_dict()
        dict2 = animal2.to_dict()
        del dict1["thing"]
        del dict2["thing"]
        self.assertEqual(dict1, dict2)

        self.assertFalse(animal1.legs is animal2.legs)
        self.assertFalse(animal1.thing is animal2.thing)

        self.assertFalse(animal1.legs[0] is animal2.legs[0])
        self.assertEqual(animal1.legs[0].to_dict(), animal2.legs[0].to_dict())
        self.assertFalse(animal1.legs[1] is animal2.legs[1])
        self.assertEqual(animal1.legs[1].to_dict(), animal2.legs[1].to_dict())
