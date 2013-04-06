from distutils.core import setup

VERSION = "1.0"

DESCRIPTION = """\
Unipath is an object-oriented front end to the file/directory functions
scattered throughout several Python library modules.  It's based on Jason
Orendorff's *path.py* but does not adhere as strictly to the underlying
functions' syntax, in order to provide more user convenience and higher-level
functionality. Unipath is stable, well-tested, and has been used in production
since 2008.
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
    license="Python",
    #platform="Multiplatform",
    keywords="os.path filename pathspec path files directories filesystem",
    classifiers=[
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3"
        ],
    )
