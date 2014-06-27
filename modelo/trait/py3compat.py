import sys

if sys.version_info[0] >= 3:
    PY3 = True

    string_types = (str,)
    unicode_type = str

    def isidentifier(s, dotted=False):
        if dotted:
            return all(isidentifier(a) for a in s.split("."))
        return s.isidentifier()

    def iteritems(d):
        return iter(d.items())
else:
    PY3 = False

    string_types = (str, unicode)
    unicode_type = unicode

    import re
    _name_re = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*$")

    def isidentifier(s, dotted=False):
        if dotted:
            return all(isidentifier(a) for a in s.split("."))
        return bool(_name_re.match(s))

    def iteritems(d):
        return d.iteritems()

iteritems.__doc__ = "An iterator over the (key, value) items of the given dictionary."

def with_metaclass(meta, *bases):
    """
    Create a base class with a metaclass.
    """
    return meta("_NewBase", bases, ())
