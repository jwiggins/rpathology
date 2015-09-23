#! /usr/bin/env python

from platform import system
from setuptools import setup, find_packages

requirements = []
if system() == 'Linux':
    requirements.append('pyelftools')

setup(name='rpathology',
      version='0.0.1',
      author='John Wiggins',
      author_email='john.wiggins@xfel.eu',
      description='A library for dealing with executable RPATHs',
      long_description='',
      packages=find_packages(),
      package_data={},
      entry_points={
          'console_scripts': [
              'rpath-fixer = rpathology.fixer:main',
              'rpath-show = rpathology.show:main',
          ],
      },
      requires=requirements,
      )
