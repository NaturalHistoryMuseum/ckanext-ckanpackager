#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-ckanpackager
# Created by the Natural History Museum in London, UK

from setuptools import find_packages, setup

__version__ = u'1.0.0-alpha'

with open(u'README.md', u'r') as f:
    __long_description__ = f.read()

setup(
    name=u'ckanext-ckanpackager',
    version=__version__,
    description=u'A CKAN extension that provides a user interface to download resources with ckanpackager.',
    long_description=__long_description__,
    classifiers=[
        u'Development Status :: 3 - Alpha',
        u'Framework :: Flask',
        u'Programming Language :: Python :: 2.7'
    ],
    keywords=u'CKAN data ckanpackager',
    author=u'Natural History Museum',
    author_email=u'data@nhm.ac.uk',
    url=u'https://github.com/NaturalHistoryMuseum/ckanext-ckanpackager',
    license=u'GNU GPLv3',
    packages=find_packages(exclude=[u'tests']),
    namespace_packages=[u'ckanext', u'ckanext.ckanpackager'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points= \
        u'''
        [ckan.plugins]
            ckan_packager=ckanext.ckanpackager.plugin:CkanPackagerPlugin

        [paste.paster_command]
            initdb=ckanext.ckanpackager.commands.initdb:CKANPackagerCommand
        ''',
    )
