"""This module exists for purists who believe that ``unipath.Path`` shouldn't
inherit from ``unipath.PathName``. It provides an ``FSPath`` class that
mimics ``Path``.  This current implementation punts by subclassing ``Path`` and
disabling the forbidden methods/properies, but there are instructions below to
make it a totally independent class.  The reason this hasn't been done yet is
it requires refactoring all methods, which is a PITA when the API is still in
flux.  

I tried to make ``unipath.Path`` independent in the way described below -- I
really did -- but it just became too cumbersome to use in applications.  For
instance, should ``.cwd``, ``.rel_path_to``, and ``.walk`` et al return
``FSPath`` objects or ``PathName`` objects?  It depends what the user
intends do do with them.  Perhaps they want to call a filesystem operation
immediately, or perhaps they want to combine it into a larger path.  Because
``PathName`` can't contain ``FSPath``, it's easier to go the other way round
and make your long-term variables ``FSPath``, and access its ``.path`` attribute
(the ``PathName`` object) as needed.  However, things get messy when you
have to deconstruct the path to modify it, then invoke the ``FSPath``
constructor again in order to call a filesystem operation:

    top_directory = FSPath("...")
    FSPath(PathName(my_directory, "subdir")).mkdir()

It gets even more verbose if one decides that the ``FSPath`` constructor should
accept only a premade ``PathName`` object rather than passing its own
arguments to the ``PathName`` constructor:

    top_directory = FSPath(PathName("..."))

This module exists for demonstration and so people can compare ``Path`` vs
``FSPath`` side by side. I (Mike Orr) personally expect to use ``Path`` 
so that's where the bulk of my development effort will go.  If the ``FSPath``
model is chosen for Python 3000's stdlib, it's possible that the API will
diverge from ``Path`` and they will end up as totally separate modules with
different maintainers.

(c) 2006 by Mike Orr <sluggoster@gmail.com>.  
Permission granted to redistribute, modify, and include in commercial or
noncommerical products under the terms of the Python license (i.e., the "PSF
license agreement for Python 2.3", in section B of
http://www.python.org/download/releases/2.3.2/license/).
See unipath.py for history, credits, and documentation.

A test suite is available in unipath_test.py.
 
HOW TO MAKE FSPath NOT SUBCLASS unipath.Path
============================================

1) Subclass ``object`` instead of ``unipath.Path``.
2) Add the ``.__init__`` method and the other code below.
3) Add all ``unipath.Path`` methods and refactor them to pass ``self.path``
instead of ``self`` to the ``os.*`` and ``shutil`` functions.


# THIS CODE IS PART OF THE DOCSTRING!
def __init__(self, *args):
   if len(args) == 1 and isinstance(args[0], Path):
       if args[0].pathlib is os.path:
           self.path = args[0]
       else:
           os.path.__name__, args[0]
           reason = "arg is a path for a non-%s platform: %s"
           raise TypeError(reason % tup)
   else:
       self.path = Path(*args)

def __hash__(self):
  return self.path.__hash__()

__slots__ = ["path"]
# END CODE INCLUDED IN DOCSTRING


CHANGELOG
=========
2006-XX-XX    Initial release.
"""

from unipath import PathName
from unipath import Path as _Path

class FSPath(_Path):
    """A unipath Path object that cannot access PathName methods or
       properties or string methods via inheritance.
    """

    def __init__(self, *args, **kw):
        _Path.__init__(self, *args, **kw)
        self.path = self  # For applications to access the PathName object.

    def __getattribute__(self, attr):
        """Disable access to PathName methods/properties and string methods.
           (The latter happens implictly because Path inherits from str or
           unicode.) Attributes beginning with "__" are not disabled to avoid
           messing up Python special methods.
        """
        if not attr.startswith("__") and attr in dir(_Path):
            raise AttributeError("use a PathName object for '%s'" % attr)
        return _Path.__getattr__(self, attr)

