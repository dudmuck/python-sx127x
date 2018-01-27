
#!/usr/bin/env python

from distutils.core import setup, Extension

version = "0.1"

classifiers = ['Development Status :: 5 - Production/Stable',
               'Operating System :: POSIX :: Linux',
               'License :: OSI Approved :: MIT license',
               'Intended Audience :: Developers',
               'Programming Language :: Python :: 2.6',
               'Programming Language :: Python :: 2.7',
               'Topic :: Software Development',
               'Topic :: System :: Hardware',
               'Topic :: System :: Hardware :: Hardware Drivers']

setup(  name            = "python-sx127x",
        version         = version,
        description     = "Python driver for sx1276 and sx1272",
        long_description= open('README.md').read() + "\n" + open('CHANGELOG.md').read(),
        author          = "Wayne Roberts",
        author_email    = "wroberts@semtech.com",
        maintainer      = "Wayne Roberts",
        maintainer_email= "wroberts@semtech.com",
        license         = "MIT",
        packages        = find_packages(exclude=['contrib', 'docs', 'tests', 'examples']), 
        install_requires = ['py-spidev'],
        classifiers     = classifiers,
        url             = "http://github.com/dudmuck/python-sx127x",
        ext_modules     = [Extension("spidev", ["spidev_module.c"])]
)

