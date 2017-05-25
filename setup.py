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
      version='0.0.3',
      license='MIT',
      author='John Wiggins',
      author_email='john.wiggins@xfel.eu',
      description='A library for dealing with executable RPATHs',
      long_description='',
      url='https://github.com/jwiggins/rpathology',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Libraries',
          'Operating System :: POSIX',
          'Operating System :: Unix',
          'Operating System :: MacOS',
      ],
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
