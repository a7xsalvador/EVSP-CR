from setuptools import setup
from Cython.Build import cythonize

setup(
    name='shortest_paths',
    ext_modules=cythonize("shortest_paths.pyx"),
)
