def add_article(name):
    """
    Returns a string containing the correct indefinite article ("a" or "an")
    prefixed to the specific string.
    """
    if name[:1].lower() in 'aeiou':
        return "an " + name
    else:
        return "a " + name

def class_of(obj):
    """
    Returns a string containing the class name of an object with the correct
    indefinite article ("a" or "an") preceding it (e.g., "an Image", "a
    PlotValue").
    """
    if isinstance(obj, basestring):
        return add_article(obj)
    else:
        return add_article(obj.__class__.__name__)

def import_item(name):
    """
    Import and return ``bar`` given the string ``foo.bar``.

    Calling ``bar = import_item("foo.bar")`` is the functional equivalent of
    executing the code ``from foo import bar``.

    :param name: fully qualified name (FQN) of the module/package being imported
    :type name: str
    :return: imported module
    :rtype: module
    """
    parts = name.rsplit('.', 1)
    if len(parts) == 2:
        # called with 'foo.bar....'
        package, obj = parts
        module = __import__(package, fromlist=[obj])
        try:
            pak = module.__dict__[obj]
        except KeyError:
            raise ImportError('No module named %s' % obj)
        return pak
    else:
        # called with un-dotted string
        return __import__(parts[0])

def repr_type(obj):
    """
    Return a string representation of a value and its type for readable error
    messages.
    """
    the_type = type(obj)
    if hasattr(the_type, "__name__") and the_type.__name__ == "InstanceType":
        # old-style class
        the_type = obj.__class__
    msg = "%r %r" % (obj, the_type)
    return msg
