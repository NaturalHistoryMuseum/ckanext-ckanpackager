# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-ckanpackager
# Created by the Natural History Museum in London, UK

from setuptools import find_packages, setup

version = u'0.2'

setup(
    name=u'ckanext-ckanpackager',
    version=version,
    description=u'CKAN extension to provide resource downloads using ckanpackager',
    url=u'https://github.com/NaturalHistoryMuseum/ckanext-ckanpackager',
    packages=find_packages(),
    namespace_packages=[u'ckanext', u'ckanext.ckanpackager'],
    entry_points=u'''
    [ckan.plugins]
    ckanpackager = ckanext.ckanpackager.plugin:CkanPackagerPlugin
    [paste.paster_command]
    initdb=ckanext.ckanpackager.commands.initdb:CKANPackagerCommand
    ''',
    )
