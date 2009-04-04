from distutils.core import setup

VERSION = "0.2.1"

DESCRIPTION = """\
Unipath is an object-oriented approach to file/pathname 
manipulations and filesystem calls, an alternative to ``os.path.*``,
``shutil.*``, and some ``os.*`` functions.  It's based on
Orendorff's path.py but has been refactored to make application code
more concise, by focusing on what the programmer wants to do rather
than on low-level operations exactly like the C library.  For
instance:

- ``p.mkdir()`` succeeds silently if the directory already exists, and
- ``p.mkdir(True)`` creates intermediate directories a la
  ``os.makedirs``.   
- ``p.rmtree(parents=True)`` combines ``shutil.rmtree``,
  ``os.path.isdir``, ``os.remove``, and ``os.removedirs``, to
  recursively remove whatever it is if it exists.  
-  ``p.read_file("rb")`` returns the file's contents in binary mode.  
- ``p.needs_update([other_path1, ...])`` returns True if p doesn't
  exist or has an older timestamp than any of the others.
- extra convenience functions in the ``unipath.tools`` module.
  ``dict2dir`` creates a directory hierarchy described by a ``dict``.
  ``dump_path`` displays an ASCII tree of a directory hierarchy.

Unipath has a ``Path`` class for abstract pathname manipulations
(``p.parent``, ``p.expand()``), and a ``FSPath`` subclass for
filesystem calls (all the ones above).  You can do "from unipath
import FSPath as Path" and forget about the distinction, or use the
``Path`` class and be confident you'll never access the filesystem.
The ``Path`` class is also being proposed as an addition to the
standard libary (``os.path.Path``).  Compare::

    # Reference a file that's two directories above another file.
    p = os.path.join(os.path.dirname(os.path.dirname("/A/B/C")), "file.txt")
    p = Path("A/B/C").parent.parent.child("file.txt")
    p = Path("A/B/C").ancestor(2).child("file.txt")
    p0 = Path("/A/B/C");  p = Path(p0.parent.parent, "file.txt")

    # Change the extension of a path.
    p = os.path.splitext("image.jpg")[0] + ".png"
    p = Path("image.jpg").name + ".png"

Documentation is in the README and on the
`website <http://sluggo.scrapping.cc/python/unipath/>`__.

Unipath is in early alpha release so the API may change as it get
greater use in the "real world".  Unipath comes with extensive
unittests, and has been tested on Python 2.5 and 2.4.4 on Linux.
Feedback and Windows/Macintosh testers are encouraged.
"""

setup(
    name="Unipath", 
    version=VERSION, 
    description="Object-oriented alternative to os/os.path/shutil",
    long_description=DESCRIPTION,
    author="Mike Orr",
    author_email="sluggoster@gmail.com",
    url="http://sluggo.scrapping.cc/python/unipath/",
    download_url=
        "http://sluggo.scrapping.cc/python/unipath/Unipath-%s.tar.gz" % VERSION,
    packages=["unipath"],
    license="Python",
    #platform="Multiplatform",
    keywords="os.path filename pathspec path files directories filesystem",
    classifiers=[
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        ],
    )
