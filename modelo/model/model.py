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
        # get a dictionary of traits based on the class definition
        traits = self.traits()

        # process update data based on model traits
        for (trait_name, trait) in iteritems(traits):
            # skip traits that aren't going to be updated
            if trait_name not in data.keys():
                continue

            # based on input to this function
            given_value   = data[trait_name]

            # based on the existing value on the model
            current_value = getattr(self, trait_name)

            # Use this to defer assignment on to self. By default, assume it
            # should be the new value.
            deferred_value = given_value

            # The only special cases worth handling are field.Instance,
            # field.List and field.Dict, the other cases can probably be
            # handled by just directly setting the value.
            if isinstance(trait, field.Instance):
                # Use recursion to call the current model instance or value's
                # update method (Model.update) with this dictionary data.
                if isinstance(given_value, dict):
                    current_value.update(given_value)
                    deferred_value = current_value
            else:
                if isinstance(trait, field.List):
                    # make a new list
                    deferred_value = []

                    # Grab the inner trait type for this list. Could be None.
                    # This is the specific type that should be used for each of
                    # the elements of the list. In the case of None, it may be
                    # any value, although model instances can't be
                    # reconstructed in that scenario.
                    inner_trait_type = trait._trait

                    # Determine if inner_trait_type is a field.Instance, and
                    # then whether or not it is a Model.
                    is_model = False
                    if isinstance(inner_trait_type, TraitType) and hasattr(inner_trait_type, "klass"):
                        if issubclass(inner_trait_type.klass, Model):
                            is_model = True

                    # Append each value to the new list. Create new model
                    # instances if necessary.
                    for some_given_value in given_value:
                        # handle model instances that need to be created
                        if is_model:
                            # Can't use Model.update here because the list is
                            # probably unordered, and updating the wrong
                            # elements is very wrong. Another implementation
                            # could be created for ordered collections, though.
                            some_given_value = inner_trait_type.klass.create(**some_given_value)
                        deferred_value.append(some_given_value)
                elif isinstance(trait, field.Dict):
                    # TODO
                    pass

            # Set the deferred_value on to the current model at the appropriate
            # trait key (trait_name).
            setattr(self, trait_name, deferred_value)
