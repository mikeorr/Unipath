from setuptools import setup, find_packages

VERSION = "1.1"

DESCRIPTION = """\
Unipath is an object-oriented front end to the file/directory functions
scattered throughout several Python library modules.  It's based on Jason
Orendorff's *path.py* but has a friendlier API and higher-level features.
Unipath is stable, well-tested, and has been used in production since 2008.
It runs on Python 2.6+ and 3.3+.

**Version 1.1** is a bugfix release. Most notably it fixes a Unicode
incompatibility on Python 3 under Windows (or operating systems with native
Unicpde filenames). The license is changed to MIT (from the Python license).
"""

setup(
    name="Unipath", 
    version=VERSION, 
    description="Object-oriented alternative to os/os.path/shutil",
    long_description=DESCRIPTION,
    author="Mike Orr",
    author_email="sluggoster@gmail.com",
    url="https://github.com/mikeorr/Unipath",
    packages=["unipath"],
    license="MIT",
    #platform="Multiplatform",
    keywords="os.path filename pathspec path files directories filesystem",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        ],
    )
