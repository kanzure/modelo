from modelo.trait.util import (
    class_of,
    repr_type,
)

class NoDefaultSpecified(object):
    pass
NoDefaultSpecified = NoDefaultSpecified()

class Undefined(object):
    pass
Undefined = Undefined()

class TraitError(Exception):
    pass

class TraitType(object):
    """
    TraitType is the base class for all trait descriptors.

    The only magic here is in the main class :class:`Model` and
    :class:`MetaModel` which does the following:

    (1) Sets the :attr:`name` attribute for every :class:`TraitType` instance
    in the classdict to the name of the attribute.

    (2) Sets the :attr:`this_class` attribute of every :class:`TraitType`
    instance in the classdict to the *class* that declared the trait. This is
    used by the :class:`This` trait to allow subclasses to accept superclasses
    for :class:`This` values.
    """

    metadata = {}
    default_value = Undefined
    info_text = "any value"

    def __init__(self, default_value=NoDefaultSpecified, **metadata):
        """
        Create a TraitType.
        """
        if default_value is not NoDefaultSpecified:
            self.default_value = default_value

        if len(metadata) > 0:
            if len(self.metadata) > 0:
                self._metadata = self.metadata.copy()
                self._metadata.update(metadata)
            else:
                self._metadata = metadata
        else:
            self._metadata = self.metadata

    def instance_init(self, obj):
        """
        This is called by :meth:`Model.__new__` to finish initialization.

        Some stages of initialization must be delayed until the parent
        :class:`Model` instance has been created. This method is called in
        :meth:`Model.__new__` after the instance has been created.

        This method triggers the creation and validation of default values and
        also things like the resolution of str given class names in
        :class:`Type` and :class:`Instance`.

        :param obj: parent :class:`Model` instance that has just been created.
        :type obj: Model
        """
        self.set_default_value(obj)

    def _validate(self, obj, value):
        if hasattr(self, "validate"):
            return self.validate(obj, value)
        elif hasattr(self, "is_valid_for"):
            valid = self.is_valid_for(value)
            if valid:
                return value
            else:
                raise TraitError("invalid value for type: %r".format(value))
        elif hasattr(self, "value_for"):
            return self.value_for(value)
        else:
            return value

    def error(self, obj, value):
        if obj is not None:
            err = "The \"%s\" trait of %s instance must be %s, but a value of %s was specified."
            err = err % (self.name, class_of(obj), self.info_text, repr_type(value))
        else:
            err = "The \"%s\" trait must be %s, but a value of %r was specified."
            err = err % (self.name, self.info_text, repr_type(value))
        raise TraitError(err)

    def get_default_value(self):
        return self.default_value

    def set_default_value(self, obj):
        """
        Set the default value on a per instance instance basis.

        This method is called by :meth:`instance_init` to create and validate
        the default value. The creation and validation of default values must
        be delayed until the parent :class:`Model` class has been instantiated.
        """
        # Check for a deferred initializer defined in the same class as the
        # trait declaration or above.
        mro = type(obj).mro()
        meth_name = "_%s_default".format(self.name)
        for cls in mro[:mro.index(self.this_class)+1]:
            if meth_name in cls.__dict__:
                break
        else:
            # didn't find one, do static initialization
            default_value = self.get_default_value()
            new_default_value = self._validate(obj, default_value)
            obj._trait_values[self.name] = new_default_value
            return

        # complete the dynamic initialization
        obj._trait_dyn_inits[self.name] = cls.__dict__[meth_name]

    def get_metadata(self, key):
        return getattr(self, "_metadata", {}).get(key, None)

    def set_metadata(self, key, value):
        getattr(self, "_metadata", {})[key] = value

    def __get__(self, obj, cls=None):
        """
        Get the value of the trait by self.name for the instance.

        Default values are instantiated when :meth:`Model.__new__` is called.
        Thus by the time this method gets called either the default value or a
        user defined value (they called :meth:`__set__`) is in the
        :class:`Model` instance.
        """
        if obj is None:
            return self
        else:
            try:
                value = obj._trait_values[self.name]
            except KeyError:
                # check for a dynamic initializer
                if self.name in obj._trait_dyn_inits:
                    value = obj._trait_dyn_inits[self.name](obj)
                    # FIXME: do we really validate here?
                    value = self._validate(obj, value)
                    obj._trait_values[self.name] = value
                    return value
                else:
                    raise TraitError("Unexpected error in TraitType: "
                    "both default value and dynamic initializer are absent.")
            except Exception:
                # Model should call set_default_value to populate this. So this
                # should never be reached. Model calls set_default_value by
                # calling instance_init.
                raise TraitError("Unexpected error in TraitType: "
                "default value not set properly.")
            else:
                return value

    def __set__(self, obj, value):
        new_value = self._validate(obj, value)
        old_value = self.__get__(obj)
        obj._trait_values[self.name] = new_value
        # trigger trait change notification stuff here
