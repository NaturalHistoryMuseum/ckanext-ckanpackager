# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-ckanpackager
# Created by the Natural History Museum in London, UK

import logging

import ckan.model as model
from ckan.plugins import toolkit

from ..model.stat import ckanpackager_stats_table

log = logging.getLogger()


class CKANPackagerCommand(toolkit.CkanCommand):
    '''Create stats from GBIF

    paster --plugin=ckanext-ckanpackager initdb -c /etc/ckan/default/development.ini

    '''

    summary = __doc__.split(u'\n')[0]
    usage = __doc__

    def command(self):
        ''' '''
        self._load_config()
        # Create the table if it doesn't exist
        self._create_table()

    @staticmethod
    def _create_table():
        ''' '''
        if not ckanpackager_stats_table.exists(model.meta.engine):
            ckanpackager_stats_table.create(model.meta.engine)
