# coding: utf-8
import setuptools
from distutils.core import setup
from distutils.command.install import install


class cahoots_install(install):
    def run(self):
        install.run(self)

        print self.install_lib


setup (
    cmdclass = {
        'install': cahoots_install
    },
    name = 'Cahoots',
    version = '0.1.0',
    url = 'https://github.com/SerenitySoftwareLLC/cahoots',
    maintainer='Serenity Software',
    maintainer_email = 'hello@serenitysoftware.io',
    description = 'A Text Comprehension Engine in Python.',
    long_description = open('README.rst', 'r').read(),
    license = 'MIT',
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    packages = [
        'cahoots',
        'cahoots.parsers',
        'cahoots.parsers.location',
        'cahoots.parsers.measurement',
        'cahoots.parsers.programming',
    ],
    package_data = {
        'cahoots': [
            # Location
            'parsers/location/data/*.sql',
            'parsers/location/data/*.bz2',
            'parsers/location/data/location.sqlite.dist',
            'parsers/location/data/LICENSE',
            # Programming
            'parsers/programming/languages/*',
            'parsers/programming/LICENSES/*',
            'parsers/programming/trainers.zip',
            # Measurement
            'parsers/measurement/units/*',
        ]
    },
)
# python ./setup.py sdist upload
