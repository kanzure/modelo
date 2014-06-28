import inspect

import modelo.trait.py3compat as py3compat
iteritems = py3compat.iteritems

from modelo.trait.trait_type import TraitType
import modelo.trait.trait_types as field

from modelo.model.util import getmembers

class MetaModel(type):
    """
    Create the Model class.
    """

    def __new__(metacls, name, bases, classdict):
        """
        Instantiate all TraitType type attributes in the classdict and set
        their :attr:`name` attribute.
        """
        # classdict is not always a dict wtf
        if not isinstance(classdict, dict):
            classdict = dict(classdict)

        for (key, value) in iteritems(classdict):
            if isinstance(value, TraitType):
                value.name = key
            elif inspect.isclass(value):
                if issubclass(value, TraitType):
                    value_inst = value()
                    value_inst.name = key
                    classdict[key] = value_inst

        return super(MetaModel, metacls).__new__(metacls, name, bases, classdict)

    def __init__(cls, name, bases, classdict):
        """
        Set the :attr:`this_class` attribute of each TraitType in the classdict
        to the newly created class ``cls``.
        """
        # classdict is not always a dict wtf
        if not isinstance(classdict, dict):
            classdict = dict(classdict)

        for (key, value) in iteritems(classdict):
            if isinstance(value, TraitType):
                value.this_class = cls

        super(MetaModel, cls).__init__(name, bases, classdict)

class Model(py3compat.with_metaclass(MetaModel, object)):
    """
    Model allows the definition of a type where instances have a specific
    collection of other types. This is the stereotypical ORM model except
    without the database bindings. Any bindings can be used separately outside
    the context of this modeling system.
    """

    # TODO: is this necessary with the py3compat definition of Model?
    __metaclass__ = MetaModel

    def __new__(cls, *args, **kwargs):
        """
        Make the TraitType instances set their default values on the instance.
        """
        # This is needed because in python 2.6 object.__new__ only accepts the
        # cls argument.
        new_meth = super(Model, cls).__new__
        if new_meth is object.__new__:
            inst = new_meth(cls)
        else:
            inst = new_meth(cls, **kwargs)

        inst._trait_values = {}
        inst._trait_dyn_inits = {}

        # Make the TraitType instances set their default values on the
        # instance.
        for key in dir(cls):
            # Some attributes raise AttributeError like zope.interface's
            # __provides__ attributes even though they exist. This causes
            # AttributeErrors even though they are listed in dir(cls).
            try:
                value = getattr(cls, key)
            except AttributeError:
                pass
            else:
                if isinstance(value, TraitType):
                    value.instance_init(inst)

        return inst

    def __init__(self, **kwargs):
        """
        Set trait values by using the keyword arguments. Use cls.create() to
        create a new instance of this model.
        """
        super(Model, self).__init__(**kwargs)

        for (key, value) in kwargs.iteritems():
            # use setattr so that validation is triggered
            setattr(self, key, value)

    @classmethod
    def class_traits(cls):
        """
        Build a list of all the defined class traits.
        """
        members = [member for member in getmembers(cls) if isinstance(member[1], TraitType)]
        traits = dict(members)
        return traits

    def traits(self):
        """
        Create a list of all the traits on this class. To get the equivalent of
        "trait_names", call keys() on the returned dict.
        """
        members = [member for member in getmembers(self.__class__) if isinstance(member[1], TraitType)]
        traits = dict(members)
        return traits

    def __getstate__(self):
        """
        Build a dictionary of traits and their current values.
        """
        # grab all the traits
        traits = self.traits()

        # filter out transient traits
        traits = [trait for trait in traits if traits[trait].get_metadata("transient") in [None, False]]

        # build a dictionary
        # TODO: use self.__dict__ instead of self._trait_values ?
        result = dict([(traitname, self._trait_values[traitname]) for traitname in traits])

        return result

    def to_dict(self):
        """
        Build a dictionary representation of this Model instance.
        """
        state = self.__getstate__()

        for (trait_name, trait_value) in state.iteritems():
            if isinstance(trait_value, list):
                new_list = []
                for element in trait_value:
                    if isinstance(element, Model):
                        element_dict = element.to_dict()
                        new_list.append(element_dict)
                    else:
                        new_list.append(element)
                state[trait_name] = new_list
            elif isinstance(trait_value, dict):
                new_dict = {}
                for (key, value) in trait_value.iteritems():
                    if isinstance(value, Model):
                        value_dict = value.to_dict()
                        new_dict[key] = value_dict
                    else:
                        new_dict[key] = value
                state[trait_name] = new_dict
            elif isinstance(trait_value, Model):
                value_dict = trait_value.to_dict()
                state[trait_name] = value_dict

        return state

    @classmethod
    def create(cls, data=None):
        """
        Build an instance of this Model using the given data.
        """
        # allow create() calls with no input
        if not data:
            data = {}

        return cls(**data)

    def update(self, data):
        """
        Update this model instance using the given data.

        :param data: update the model with this data
        :type data: dict
        """
        for (key, value) in iteritems(data):
            pass
