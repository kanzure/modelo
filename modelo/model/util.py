import inspect

def getmembers(obj, predicate=None):
    """
    A safe version of inspect.getmembers that handles missing attributes.

    This is useful when there are descriptor based attributes that for some
    reason raise AttributeError even though they exist. This happens in
    zope.interface with the __provides__ attribute.
    """
    results = []
    for key in dir(obj):
        try:
            value = getattr(obj, key)
        except AttributeError:
            pass
        else:
            if not predicate or predicate(value):
                results.append((key, value))
    results.sort()
    return results
