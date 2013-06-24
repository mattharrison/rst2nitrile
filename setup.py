try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(name='rst2nitrile',
      version='0.1',
      author='matt harrison',
      description='utilities to create LaTex',
      scripts=['rst2nitrile.py'],
)
