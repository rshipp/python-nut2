import os
from setuptools import setup

from nut2 import __version__

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='nut2',
    version=__version__,
    py_modules=['nut2'],
    include_package_data=True,
    install_requires=[],
    license='GPL3',
    description='A Python abstraction class to access NUT servers.',
    long_description=README,
    url='https://github.com/rshipp/python-nut2',
    author='Ryan Shipp',
    author_email='python@rshipp.com',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Power (UPS)',
        'Topic :: System :: Systems Administration',
    ],
)
