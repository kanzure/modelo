import random
import unittest
import string
import sys

import modelo.model.model as model
import modelo.trait.trait_types as field

def _random_string(min=1, max=1024):
    """
    Generate a random length string (min <= len(str) < max) of random ascii chars.
    """
    return ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
                   for x in range(random.randint(min, max)))


def _random_int(min=0, max=sys.maxint):
    """
    Generate a random integer where min <= x <=max
    """
    return random.randint(min, max)


def _random_float():
    """
    Generate a random float where 0 < x < 1
    """
    return random.random()

# Type constants
STR_TYPE = 'str'
INT_TYPE = 'int'
FLOAT_TYPE = 'float'

#: Map of types to their random value generator
_random_type_gen = {STR_TYPE: _random_string,
                    INT_TYPE: _random_int,
                    FLOAT_TYPE: _random_float}


def _random_list(_type, max=100):
    """
    Generate a random list of the supplied type of length 0 < len <= max
    """
    return [_random_type_gen[_type]() for x in range(0, max)]


def _random_dict(key_type, value_type, size=10):
    """
    Generate a random dict with a specific key and value type.
    """
    d = {}
    for x in xrange(0, size):
        d[_random_type_gen[key_type]()] = _random_type_gen[value_type]()

    return d


#: A Simple model to be used for testing.  It only contains primitive field types and containers
#: of primitive types.  Each of the attribute values is randomly generated so no two test runs
#: use the same values.
class SimpleModel(model.Model):

    ##################
    # Primitive fields
    ##################
    STR = _random_string()
    str = field.String(STR)

    BOOL = True
    bool = field.Bool(BOOL)

    INT = _random_int()
    int = field.Int(INT)

    FLOAT = _random_float()
    float = field.Float(FLOAT)

    #############
    # Enum fields
    #############
    STR_ENUM = _random_list(STR_TYPE)
    STR_ENUM_DEFAULT = STR_ENUM[_random_int(0, len(STR_ENUM)-1)]
    str_enum = field.Enum(STR_ENUM, STR_ENUM_DEFAULT)

    INT_ENUM = _random_list(INT_TYPE)
    INT_ENUM_DEFAULT = INT_ENUM[_random_int(0, len(INT_ENUM)-1)]
    int_enum = field.Enum(INT_ENUM, INT_ENUM_DEFAULT)

    FLOAT_ENUM = _random_list(FLOAT_TYPE)
    FLOAT_ENUM_DEFAULT = FLOAT_ENUM[_random_int(0, len(FLOAT_ENUM)-1)]
    float_enum = field.Enum(FLOAT_ENUM, FLOAT_ENUM_DEFAULT)

    ##################
    # Container fields
    ##################

    # Lists
    STR_LIST = _random_list(STR_TYPE)
    str_list = field.List(field.String, STR_LIST)

    INT_LIST = _random_list(INT_TYPE)
    int_list = field.List(field.Int, INT_LIST)

    FLOAT_LIST = _random_list(FLOAT_TYPE)
    float_list = field.List(field.Float, FLOAT_LIST)

    # Sets
    STR_SET = set(_random_list(STR_TYPE))
    str_set = field.Set(field.String, STR_SET)

    INT_SET = set(_random_list(INT_TYPE))
    int_set = field.Set(field.Int, INT_SET)

    FLOAT_SET = set(_random_list(FLOAT_TYPE))
    float_set = field.Set(field.Float, FLOAT_SET)

    # Dicts
    STR_STR_DICT = _random_dict(STR_TYPE, STR_TYPE)
    str_str_dict = field.Dict(STR_STR_DICT)

    INT_STR_DICT = _random_dict(INT_TYPE, STR_TYPE)
    int_str_dict = field.Dict(INT_STR_DICT)

    FLOAT_STR_DICT = _random_dict(FLOAT_TYPE, STR_TYPE)
    float_str_dict = field.Dict(FLOAT_STR_DICT)

    STR_INT_DICT = _random_dict(STR_TYPE, INT_TYPE)
    str_int_dict = field.Dict(STR_INT_DICT)

    INT_INT_DICT = _random_dict(INT_TYPE, INT_TYPE)
    int_int_dict = field.Dict(INT_INT_DICT)

    FLOAT_INT_DICT = _random_dict(FLOAT_TYPE, INT_TYPE)
    float_int_dict = field.Dict(FLOAT_INT_DICT)

    STR_FLOAT_DICT = _random_dict(STR_TYPE, FLOAT_TYPE)
    str_float_dict = field.Dict(STR_FLOAT_DICT)

    INT_FLOAT_DICT = _random_dict(INT_TYPE, FLOAT_TYPE)
    int_float_dict = field.Dict(INT_FLOAT_DICT)

    FLOAT_FLOAT_DICT = _random_dict(FLOAT_TYPE, FLOAT_TYPE)
    float_float_dict = field.Dict(FLOAT_FLOAT_DICT)

#: This is the representation of the SimpleModel type as a dictionary.  It is constructed
#: using different random values than the SimpleModel class def.  We use this to constuct
#: a SimpleModel from a dictionary and verify that it is constructed properly.
SIMPLE_MODEL_AS_DICT = {
    # Primitive fields
    'bool': False,
    'str': _random_string(),
    'int': _random_int(),
    'float': _random_float(),

    # Enum fields
    'str_enum': SimpleModel.STR_ENUM_DEFAULT,
    'int_enum': SimpleModel.INT_ENUM_DEFAULT,
    'float_enum': SimpleModel.FLOAT_ENUM_DEFAULT,

    # List fields
    'str_list': _random_list(STR_TYPE),
    'int_list': _random_list(INT_TYPE),
    'float_list': _random_list(FLOAT_TYPE),

    # Set fields
    'str_set': set(_random_list(STR_TYPE)),
    'int_set': set(_random_list(INT_TYPE)),
    'float_set': set(_random_list(FLOAT_TYPE)),

    # Dict fields
    'str_str_dict': _random_dict(STR_TYPE, STR_TYPE),
    'int_str_dict': _random_dict(INT_TYPE, STR_TYPE),
    'float_str_dict': _random_dict(FLOAT_TYPE, STR_TYPE),

    'str_int_dict': _random_dict(STR_TYPE, INT_TYPE),
    'int_int_dict': _random_dict(INT_TYPE, INT_TYPE),
    'float_int_dict': _random_dict(FLOAT_TYPE, INT_TYPE),

    'str_float_dict': _random_dict(STR_TYPE, FLOAT_TYPE),
    'int_float_dict': _random_dict(INT_TYPE, FLOAT_TYPE),
    'float_float_dict': _random_dict(FLOAT_TYPE, FLOAT_TYPE)
}


class SimpleModelTests(unittest.TestCase):
    """
    """

    def test_init_default(self):
        s = SimpleModel()

        # Verify primitive types
        for _field in ['bool', 'int', 'float', 'str']:
            self.assertIsNotNone(getattr(s, _field))
            self.assertEqual(getattr(s, _field), getattr(SimpleModel, _field.upper()))

        # Verify enum types
        for _field in ['str_enum', 'int_enum', 'float_enum']:
            self.assertIsNotNone(getattr(s, _field))
            self.assertIn(getattr(s, _field), getattr(SimpleModel, _field.upper()))
            self.assertEqual(getattr(s, _field), getattr(SimpleModel, '%s_DEFAULT' % _field.upper()))

        # Verify list containers
        for _field in ['str_list', 'int_list', 'float_list']:
            self.assertIsNotNone(getattr(s, _field))
            self.assertIsInstance(getattr(s, _field), list)
            self.assertEqual(getattr(s, _field), getattr(SimpleModel, _field.upper()))

        # Verify set containers
        for _field in ['str_set', 'int_set', 'float_set']:
            self.assertIsNotNone(getattr(s, _field))
            self.assertIsInstance(getattr(s, _field), set)
            self.assertEqual(getattr(s, _field), getattr(SimpleModel, _field.upper()))

        # Veriy dict contaiers
        for _field in ['str_str_dict', 'int_str_dict', 'float_str_dict',
                       'str_int_dict', 'int_int_dict', 'float_int_dict',
                       'str_float_dict', 'int_float_dict', 'float_float_dict']:

            self.assertIsNotNone(getattr(s, _field))
            self.assertIsInstance(getattr(s, _field), dict)
            self.assertEqual(set(getattr(s, _field).keys()),
                             set(getattr(SimpleModel, _field.upper()).keys()))
            self.assertEqual(set(getattr(s, _field).values()),
                             set(getattr(SimpleModel, _field.upper()).values()))

    def test_to_dict(self):
        s = SimpleModel()
        s_as_dict = s.to_dict()

        self.assertIsNotNone(s_as_dict)
        self.assertIsInstance(s_as_dict, dict)

        # Verify primitive types
        for _field in ['bool', 'int', 'float', 'str']:
            self.assertIsNotNone(s_as_dict[_field])
            self.assertEqual(s_as_dict[_field], getattr(s, _field))

        # Verify enum types
        for _field in ['str_enum', 'int_enum', 'float_enum']:
            self.assertIsNotNone(s_as_dict[_field])
            self.assertIn(s_as_dict[_field], getattr(s, _field.upper()))
            self.assertEqual(s_as_dict[_field], getattr(s, '%s_DEFAULT' % _field.upper()))

        # Verify list containers
        for _field in ['str_list', 'int_list', 'float_list']:
            self.assertIsNotNone(s_as_dict[_field])
            self.assertIsInstance(s_as_dict[_field], list)
            self.assertEqual(s_as_dict[_field], getattr(s, _field))

        # Verify the set containers
        for _field in ['str_set', 'int_set', 'float_set']:
            self.assertIsNotNone(s_as_dict[_field])
            self.assertIsInstance(s_as_dict[_field], set)
            self.assertEqual(s_as_dict[_field], getattr(s, _field))

        # Verify the dict containers
        for _field in ['str_str_dict', 'int_str_dict', 'float_str_dict',
                       'str_int_dict', 'int_int_dict', 'float_int_dict',
                       'str_float_dict', 'int_float_dict', 'float_float_dict']:

            self.assertIsNotNone(s_as_dict[_field])
            self.assertIsInstance(s_as_dict[_field], dict)
            self.assertEqual(set(s_as_dict[_field].keys()), set(getattr(s, _field).keys()))
            self.assertEqual(set(s_as_dict[_field].values()), set(getattr(s, _field).values()))

    def test_create(self):
        as_dict = SIMPLE_MODEL_AS_DICT
        s = SimpleModel.create(as_dict)

        self.assertIsNotNone(s)
        self.assertIsInstance(s, SimpleModel)

        # Verify primitive fields
        for _field in ['str', 'bool', 'int', 'float']:
            self.assertIsNotNone(getattr(s, _field))
            self.assertEqual(getattr(s, _field), as_dict[_field])

        # Verify enum fields
        for _field in ['str_enum', 'int_enum', 'float_enum']:
            self.assertIsNotNone(getattr(s, _field))
            self.assertIn(getattr(s, _field), getattr(s, _field.upper()))
            self.assertEqual(getattr(s, _field), getattr(s, '%s_DEFAULT' % _field.upper()))

        # Verify list containers
        for _field in ['str_list', 'int_list', 'float_list']:
            self.assertIsNotNone(getattr(s, _field))
            self.assertIsInstance(getattr(s, _field), list)
            self.assertEqual(getattr(s, _field), as_dict[_field])

        # Verify set containers
        for _field in ['str_set', 'int_set', 'float_set']:
            self.assertIsNotNone(getattr(s, _field))
            self.assertIsInstance(getattr(s, _field), set)
            self.assertEqual(getattr(s, _field), as_dict[_field])

        # Verify dict fields
        for _field in ['str_str_dict', 'int_str_dict', 'float_str_dict',
                       'str_int_dict', 'int_int_dict', 'float_int_dict',
                       'str_float_dict', 'int_float_dict', 'float_float_dict']:

            self.assertIsNotNone(getattr(s, _field))
            self.assertIsInstance(getattr(s, _field), dict)
            self.assertEqual(getattr(s, _field).keys(), as_dict[_field].keys())
            self.assertEqual(getattr(s, _field).values(), as_dict[_field].values())
