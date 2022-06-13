#!/usr/bin/env python3
# encoding: utf-8
#
# This file is part of ckanext-ckanpackager
# Created by the Natural History Museum in London, UK

from setuptools import find_packages, setup

__version__ = '2.1.2'

with open('README.md', 'r') as f:
    __long_description__ = f.read()

setup(
    name='ckanext-ckanpackager',
    version=__version__,
    description='A CKAN extension that provides a user interface to download resources with ckanpackager.',
    long_description=__long_description__,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='CKAN data ckanpackager',
    author='Natural History Museum',
    author_email='data@nhm.ac.uk',
    url='https://github.com/NaturalHistoryMuseum/ckanext-ckanpackager',
    license='GNU GPLv3',
    packages=find_packages(exclude=['tests']),
    namespace_packages=['ckanext', 'ckanext.ckanpackager'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'requests>=1.1.0',
    ],
    entry_points= \
        '''
        [ckan.plugins]
            ckanpackager=ckanext.ckanpackager.plugin:CkanPackagerPlugin
        ''',
    )
