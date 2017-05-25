#! /usr/bin/env python

from platform import system
from setuptools import setup, find_packages

requirements = []
sys_os = system().lower()
if sys_os == 'linux':
    requirements.append('pyelftools')
elif sys_os == 'darwin':
    requirements.append('machotools')

setup(name='rpathology',
      version='0.0.2',
      author='John Wiggins',
      author_email='john.wiggins@xfel.eu',
      description='A library for dealing with executable RPATHs',
      long_description='',
      packages=find_packages(),
      package_data={},
      entry_points={
          'console_scripts': [
              'rpath-fixer = rpathology.fixer:main',
              'rpath-missing = rpathology.list:main',
              'rpath-show = rpathology.show:main',
          ],
      },
      requires=requirements,
      )
