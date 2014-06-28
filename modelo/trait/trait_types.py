"""
Various subclasses of TraitType.
"""
import sys
import inspect
import re
import types

from types import (
    FunctionType,
    MethodType,
)

try:
    from types import (
        ClassType,
        InstanceType,
    )
    ClassTypes = (ClassType, type)
except:
    ClassTypes = (type,)

SequenceTypes = (list, tuple, set, frozenset)

import modelo.trait.py3compat as py3compat

from modelo.trait.util import (
    class_of,
    import_item,
)

from modelo.trait.trait_type import TraitType

def is_trait(maybe_trait):
    """
    Return whether the given value is an instance or subclass of TraitType.
    """
    return (isinstance(maybe_trait, TraitType) or
           (isinstance(maybe_trait, type) and issubclass(maybe_trait, TraitType)))

class DefaultValueGenerator(object):
    """
    A class for generating new default value instances.
    """

    def __init__(self, *args, **kw):
        self.args = args
        self.kw = kw

    def generate(self, klass):
        return klass(*self.args, **self.kw)

class ClassBasedTraitType(TraitType):
    """
    A trait with error reporting for Type, Instance and This.
    """

    def error(self, obj, value):
        kind = type(value)
        if (not py3compat.PY3) and kind is InstanceType:
            msg = 'class %s' % value.__class__.__name__
        else:
            msg = '%s (i.e. %s)' % ( str( kind )[1:-1], repr( value ) )

        if obj is not None:
            e = "The '%s' trait of %s instance must be %s, but a value of %s was specified." \
                % (self.name, class_of(obj),
                   self.info(), msg)
        else:
            e = "The '%s' trait must be %s, but a value of %r was specified." \
                % (self.name, self.info(), msg)

        raise TraitError(e)

class Type(ClassBasedTraitType):
    """
    A trait whose value must be a subclass of a specified class.
    """

    def __init__ (self, default_value=None, klass=None, allow_none=True, **metadata ):
        """
        Construct a Type trait.

        A Type trait specifies that its values must be subclasses of
        a particular class.

        If only ``default_value`` is given, it is used for the ``klass`` as
        well.

        Parameters
        ----------
        default_value : class, str or None
            The default value must be a subclass of klass.  If an str,
            the str must be a fully specified class name, like 'foo.bar.Bah'.
            The string is resolved into real class, when the parent
            :class:`HasTraits` class is instantiated.
        klass : class, str, None
            Values of this trait must be a subclass of klass.  The klass
            may be specified in a string like: 'foo.bar.MyClass'.
            The string is resolved into real class, when the parent
            :class:`HasTraits` class is instantiated.
        allow_none : boolean
            Indicates whether None is allowed as an assignable value. Even if
            ``False``, the default value may be ``None``.
        """
        if default_value is None:
            if klass is None:
                klass = object
        elif klass is None:
            klass = default_value

        if not (inspect.isclass(klass) or isinstance(klass, py3compat.string_types)):
            raise TraitError("A Type trait must specify a class.")

        self.klass       = klass
        self._allow_none = allow_none

        super(Type, self).__init__(default_value, **metadata)

    def validate(self, obj, value):
        """Validates that the value is a valid object instance."""
        try:
            if issubclass(value, self.klass):
                return value
        except:
            if (value is None) and (self._allow_none):
                return value

        self.error(obj, value)

    def info(self):
        """ Returns a description of the trait."""
        if isinstance(self.klass, py3compat.string_types):
            klass = self.klass
        else:
            klass = self.klass.__name__
        result = 'a subclass of ' + klass
        if self._allow_none:
            return result + ' or None'
        return result

    def instance_init(self, obj):
        self._resolve_classes()
        super(Type, self).instance_init(obj)

    def _resolve_classes(self):
        if isinstance(self.klass, py3compat.string_types):
            self.klass = import_item(self.klass)
        if isinstance(self.default_value, py3compat.string_types):
            self.default_value = import_item(self.default_value)

    def get_default_value(self):
        return self.default_value

class Instance(ClassBasedTraitType):
    """
    A trait whose value must be an instance of the specified class. The value
    can also be an instance of a subclass of the specified class.
    """

    def __init__(self, klass=None, args=None, kw=None,
                 allow_none=True, **metadata ):
        """Construct an Instance trait.

        This trait allows values that are instances of a particular
        class or its sublclasses.  Our implementation is quite different
        from that of enthough.traits as we don't allow instances to be used
        for klass and we handle the ``args`` and ``kw`` arguments differently.

        Parameters
        ----------
        klass : class, str
            The class that forms the basis for the trait.  Class names
            can also be specified as strings, like 'foo.bar.Bar'.
        args : tuple
            Positional arguments for generating the default value.
        kw : dict
            Keyword arguments for generating the default value.
        allow_none : bool
            Indicates whether None is allowed as a value.

        Notes
        -----
        If both ``args`` and ``kw`` are None, then the default value is None.
        If ``args`` is a tuple and ``kw`` is a dict, then the default is
        created as ``klass(*args, **kw)``.  If either ``args`` or ``kw`` is
        not (but not both), None is replace by ``()`` or ``{}``.
        """

        self._allow_none = allow_none

        if (klass is None) or (not (inspect.isclass(klass) or isinstance(klass, py3compat.string_types))):
            raise TraitError('The klass argument must be a class'
                                ' you gave: %r' % klass)
        self.klass = klass

        # self.klass is a class, so handle default_value
        if args is None and kw is None:
            default_value = None
        else:
            if args is None:
                # kw is not None
                args = ()
            elif kw is None:
                # args is not None
                kw = {}

            if not isinstance(kw, dict):
                raise TraitError("The 'kw' argument must be a dict or None.")
            if not isinstance(args, tuple):
                raise TraitError("The 'args' argument must be a tuple or None.")

            default_value = DefaultValueGenerator(*args, **kw)

        super(Instance, self).__init__(default_value, **metadata)

    def validate(self, obj, value):
        if value is None:
            if self._allow_none:
                return value
            self.error(obj, value)

        if isinstance(value, self.klass):
            return value
        else:
            self.error(obj, value)

    def info(self):
        if isinstance(self.klass, py3compat.string_types):
            klass = self.klass
        else:
            klass = self.klass.__name__
        result = class_of(klass)
        if self._allow_none:
            return result + ' or None'

        return result

    def instance_init(self, obj):
        self._resolve_classes()
        super(Instance, self).instance_init(obj)

    def _resolve_classes(self):
        if isinstance(self.klass, py3compat.string_types):
            self.klass = import_item(self.klass)

    def get_default_value(self):
        """Instantiate a default value instance.

        This is called when the containing HasTraits classes'
        :meth:`__new__` method is called to ensure that a unique instance
        is created for each HasTraits instance.
        """
        dv  = self.default_value
        if isinstance(dv, DefaultValueGenerator):
            return dv.generate(self.klass)
        else:
            return dv

class This(ClassBasedTraitType):
    """
    A trait for instances of the class containing this trait.

    Because how how and when class bodies are executed, the ``This``
    trait can only have a default value of None.  This, and because we
    always validate default values, ``allow_none`` is *always* true.
    """

    info_text = 'an instance of the same type as the receiver or None'

    def __init__(self, **metadata):
        super(This, self).__init__(None, **metadata)

    def validate(self, obj, value):
        # What if value is a superclass of obj.__class__?  This is
        # complicated if it was the superclass that defined the This
        # trait.
        if isinstance(value, self.this_class) or (value is None):
            return value
        else:
            self.error(obj, value)

class Any(TraitType):
    default_value = None
    info_text = "any value"

class Int(TraitType):
    """
    An integer trait.
    """

    default_value = 0
    info_text = "an int"

    def validate(self, obj, value):
        if isinstance(value, int):
            return value
        self.error(obj, value)

class CInt(Int):
    """A casting version of the int trait."""

    def validate(self, obj, value):
        try:
            return int(value)
        except:
            self.error(obj, value)

if py3compat.PY3:
    Long, CLong = Int, CInt
    Integer = Int
else:
    class Long(TraitType):
        """A long integer trait."""

        default_value = 0
        info_text = 'a long'

        def validate(self, obj, value):
            if isinstance(value, long):
                return value
            if isinstance(value, int):
                return long(value)
            self.error(obj, value)


    class CLong(Long):
        """A casting version of the long integer trait."""

        def validate(self, obj, value):
            try:
                return long(value)
            except:
                self.error(obj, value)

    class Integer(TraitType):
        """An integer trait.

        Longs that are unnecessary (<= sys.maxint) are cast to ints."""

        default_value = 0
        info_text = 'an integer'

        def validate(self, obj, value):
            if isinstance(value, int):
                return value
            if isinstance(value, long):
                # downcast longs that fit in int:
                # note that int(n > sys.maxint) returns a long, so
                # we don't need a condition on this cast
                return int(value)
            if sys.platform == "cli":
                from System import Int64
                if isinstance(value, Int64):
                    return int(value)
            self.error(obj, value)

class Float(TraitType):
    """A float trait."""

    default_value = 0.0
    info_text = 'a float'

    def validate(self, obj, value):
        if isinstance(value, float):
            return value
        if isinstance(value, int):
            return float(value)
        self.error(obj, value)

class CFloat(Float):
    """A casting version of the float trait."""

    def validate(self, obj, value):
        try:
            return float(value)
        except:
            self.error(obj, value)

class Complex(TraitType):
    """A trait for complex numbers."""

    default_value = 0.0 + 0.0j
    info_text = 'a complex number'

    def validate(self, obj, value):
        if isinstance(value, complex):
            return value
        if isinstance(value, (float, int)):
            return complex(value)
        self.error(obj, value)

class CComplex(Complex):
    """A casting version of the complex number trait."""

    def validate (self, obj, value):
        try:
            return complex(value)
        except:
            self.error(obj, value)

# We should always be explicit about whether we're using bytes or unicode, both
# for Python 3 conversion and for reliable unicode behaviour on Python 2. So
# we don't have a Str type.
class Bytes(TraitType):
    """A trait for byte strings."""

    default_value = b''
    info_text = 'a bytes object'

    def validate(self, obj, value):
        if isinstance(value, bytes):
            return value
        self.error(obj, value)

class CBytes(Bytes):
    """A casting version of the byte string trait."""

    def validate(self, obj, value):
        try:
            return bytes(value)
        except:
            self.error(obj, value)

class Unicode(TraitType):
    """A trait for unicode strings."""

    default_value = u''
    info_text = 'a unicode string'

    def validate(self, obj, value):
        if isinstance(value, py3compat.unicode_type):
            return value
        if isinstance(value, bytes):
            try:
                return value.decode('ascii', 'strict')
            except UnicodeDecodeError:
                msg = "Could not decode {!r} for unicode trait '{}' of {} instance."
                raise TraitError(msg.format(value, self.name, class_of(obj)))
        self.error(obj, value)

# use unicode everywhere
String = Unicode

class CUnicode(Unicode):
    """A casting version of the unicode trait."""

    def validate(self, obj, value):
        try:
            return py3compat.unicode_type(value)
        except:
            self.error(obj, value)

class ObjectName(TraitType):
    """A string holding a valid object name in this version of Python.

    This does not check that the name exists in any scope."""
    info_text = "a valid object identifier in Python"

    if py3compat.PY3:
        # Python 3:
        coerce_str = staticmethod(lambda _, s: s)

    else:
        # Python 2:
        def coerce_str(self, obj, value):
            "In Python 2, coerce ascii-only unicode to str"
            if isinstance(value, unicode):
                try:
                    return str(value)
                except UnicodeEncodeError:
                    self.error(obj, value)
            return value

    def validate(self, obj, value):
        value = self.coerce_str(obj, value)

        if isinstance(value, str) and py3compat.isidentifier(value):
            return value
        self.error(obj, value)

class DottedObjectName(ObjectName):
    """A string holding a valid dotted object name in Python, such as A.b3._c"""
    def validate(self, obj, value):
        value = self.coerce_str(obj, value)

        if isinstance(value, str) and py3compat.isidentifier(value, dotted=True):
            return value
        self.error(obj, value)

class Bool(TraitType):
    """A boolean (True, False) trait."""

    default_value = False
    info_text = 'a boolean'

    def validate(self, obj, value):
        if isinstance(value, bool):
            return value
        self.error(obj, value)

class CBool(Bool):
    """A casting version of the boolean trait."""

    def validate(self, obj, value):
        try:
            return bool(value)
        except:
            self.error(obj, value)

class Enum(TraitType):
    """An enum that whose value must be in a given sequence."""

    def __init__(self, values, default_value=None, allow_none=True, **metadata):
        self.values = values
        self._allow_none = allow_none
        super(Enum, self).__init__(default_value, **metadata)

    def validate(self, obj, value):
        if value is None:
            if self._allow_none:
                return value

        if value in self.values:
            return value
        self.error(obj, value)

    def info(self):
        """ Returns a description of the trait."""
        result = 'any of ' + repr(self.values)
        if self._allow_none:
            return result + ' or None'
        return result

class CaselessStrEnum(Enum):
    """An enum of strings that are caseless in validate."""

    def validate(self, obj, value):
        if value is None:
            if self._allow_none:
                return value

        if not isinstance(value, py3compat.string_types):
            self.error(obj, value)

        for v in self.values:
            if v.lower() == value.lower():
                return v
        self.error(obj, value)

class Container(Instance):
    """An instance of a container (list, set, etc.)

    To be subclassed by overriding klass.
    """
    klass = None
    _valid_defaults = SequenceTypes
    _trait = None

    def __init__(self, trait=None, default_value=None, allow_none=True,
                **metadata):
        """Create a container trait type from a list, set, or tuple.

        The default value is created by doing ``List(default_value)``,
        which creates a copy of the ``default_value``.

        ``trait`` can be specified, which restricts the type of elements
        in the container to that TraitType.

        If only one arg is given and it is not a Trait, it is taken as
        ``default_value``:

        ``c = List([1, 2, 3])``

        Parameters
        ----------

        trait : TraitType [ optional ]
            the type for restricting the contents of the Container.  If unspecified,
            types are not checked.

        default_value : SequenceType [ optional ]
            The default value for the Trait.  Must be list/tuple/set, and
            will be cast to the container type.

        allow_none : Bool [ default True ]
            Whether to allow the value to be None

        **metadata : any
            further keys for extensions to the Trait (e.g. config)

        """
        # allow List([values]):
        if default_value is None and not is_trait(trait):
            default_value = trait
            trait = None

        if default_value is None:
            args = ()
        elif isinstance(default_value, self._valid_defaults):
            args = (default_value, )
        else:
            raise TypeError('default value of %s was %s' %(self.__class__.__name__, default_value))

        if is_trait(trait):
            self._trait = trait() if isinstance(trait, type) else trait
            self._trait.name = 'element'
        elif trait is not None:
            raise TypeError("`trait` must be a Trait or None, got %s"%repr_type(trait))

        super(Container, self).__init__(klass=self.klass, args=args,
                                  allow_none=allow_none, **metadata)

    def element_error(self, obj, element, validator):
        e = "Element of the '%s' trait of %s instance must be %s, but a value of %s was specified." \
            % (self.name, class_of(obj), validator.info(), repr_type(element))
        raise TraitError(e)

    def validate(self, obj, value):
        value = super(Container, self).validate(obj, value)
        if value is None:
            return value

        value = self.validate_elements(obj, value)

        return value

    def validate_elements(self, obj, value):
        validated = []
        if self._trait is None or isinstance(self._trait, Any):
            return value
        for v in value:
            try:
                v = self._trait.validate(obj, v)
            except TraitError:
                self.element_error(obj, v, self._trait)
            else:
                validated.append(v)
        return self.klass(validated)

class List(Container):
    """An instance of a Python list."""
    klass = list

    def __init__(self, trait=None, default_value=None, minlen=0, maxlen=sys.maxsize,
                 allow_none=True, **metadata):
        """Create a List trait type from a list, set, or tuple.

        The default value is created by doing ``List(default_value)``,
        which creates a copy of the ``default_value``.

        ``trait`` can be specified, which restricts the type of elements
        in the container to that TraitType.

        If only one arg is given and it is not a Trait, it is taken as
        ``default_value``:

        ``c = List([1, 2, 3])``

        Parameters
        ----------

        trait : TraitType [ optional ]
            the type for restricting the contents of the Container.  If unspecified,
            types are not checked.

        default_value : SequenceType [ optional ]
            The default value for the Trait.  Must be list/tuple/set, and
            will be cast to the container type.

        minlen : Int [ default 0 ]
            The minimum length of the input list

        maxlen : Int [ default sys.maxsize ]
            The maximum length of the input list

        allow_none : Bool [ default True ]
            Whether to allow the value to be None

        **metadata : any
            further keys for extensions to the Trait (e.g. config)

        """
        self._minlen = minlen
        self._maxlen = maxlen
        super(List, self).__init__(trait=trait, default_value=default_value,
                                allow_none=allow_none, **metadata)

    def length_error(self, obj, value):
        e = "The '%s' trait of %s instance must be of length %i <= L <= %i, but a value of %s was specified." \
            % (self.name, class_of(obj), self._minlen, self._maxlen, value)
        raise TraitError(e)

    def validate_elements(self, obj, value):
        length = len(value)
        if length < self._minlen or length > self._maxlen:
            self.length_error(obj, value)

        return super(List, self).validate_elements(obj, value)

class Set(Container):
    """An instance of a Python set."""
    klass = set

class Tuple(Container):
    """An instance of a Python tuple."""
    klass = tuple

    def __init__(self, *traits, **metadata):
        """Tuple(*traits, default_value=None, allow_none=True, **medatata)

        Create a tuple from a list, set, or tuple.

        Create a fixed-type tuple with Traits:

        ``t = Tuple(Int, Str, CStr)``

        would be length 3, with Int, Str, CStr for each element.

        If only one arg is given and it is not a Trait, it is taken as
        default_value:

        ``t = Tuple((1, 2, 3))``

        Otherwise, ``default_value`` *must* be specified by keyword.

        Parameters
        ----------

        *traits : TraitTypes [ optional ]
            the tsype for restricting the contents of the Tuple.  If unspecified,
            types are not checked. If specified, then each positional argument
            corresponds to an element of the tuple.  Tuples defined with traits
            are of fixed length.

        default_value : SequenceType [ optional ]
            The default value for the Tuple.  Must be list/tuple/set, and
            will be cast to a tuple. If `traits` are specified, the
            `default_value` must conform to the shape and type they specify.

        allow_none : Bool [ default True ]
            Whether to allow the value to be None

        **metadata : any
            further keys for extensions to the Trait (e.g. config)

        """
        default_value = metadata.pop('default_value', None)
        allow_none = metadata.pop('allow_none', True)

        # allow Tuple((values,)):
        if len(traits) == 1 and default_value is None and not is_trait(traits[0]):
            default_value = traits[0]
            traits = ()

        if default_value is None:
            args = ()
        elif isinstance(default_value, self._valid_defaults):
            args = (default_value, )
        else:
            raise TypeError('default value of %s was %s' %(self.__class__.__name__, default_value))

        self._traits = []
        for trait in traits:
            t = trait() if isinstance(trait, type) else trait
            t.name = 'element'
            self._traits.append(t)

        if self._traits and default_value is None:
            # don't allow default to be an empty container if length is specified
            args = None
        super(Container, self).__init__(klass=self.klass, args=args,
                                  allow_none=allow_none, **metadata)

    def validate_elements(self, obj, value):
        if not self._traits:
            # nothing to validate
            return value
        if len(value) != len(self._traits):
            e = "The '%s' trait of %s instance requires %i elements, but a value of %s was specified." \
                % (self.name, class_of(obj), len(self._traits), repr_type(value))
            raise TraitError(e)

        validated = []
        for t, v in zip(self._traits, value):
            try:
                v = t.validate(obj, v)
            except TraitError:
                self.element_error(obj, v, t)
            else:
                validated.append(v)
        return tuple(validated)

class Dict(Instance):
    """An instance of a Python dict."""

    def __init__(self, default_value=None, allow_none=True, **metadata):
        """Create a dict trait type from a dict.

        The default value is created by doing ``dict(default_value)``,
        which creates a copy of the ``default_value``.
        """
        if default_value is None:
            args = ((),)
        elif isinstance(default_value, dict):
            args = (default_value,)
        elif isinstance(default_value, SequenceTypes):
            args = (default_value,)
        else:
            raise TypeError('default value of Dict was %s' % default_value)

        super(Dict, self).__init__(klass=dict, args=args,
                                  allow_none=allow_none, **metadata)

class CRegExp(TraitType):
    """A casting compiled regular expression trait.

    Accepts both strings and compiled regular expressions. The resulting
    attribute will be a compiled regular expression."""

    info_text = 'a regular expression'

    def validate(self, obj, value):
        try:
            return re.compile(value)
        except:
            self.error(obj, value)
