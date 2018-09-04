# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-ckanpackager
# Created by the Natural History Museum in London, UK

import logging

from ckanext.ckanpackager.model.stat import Base

import ckan.model as model
from ckan.lib.cli import CkanCommand

log = logging.getLogger()


class CKANPackagerCommand(CkanCommand):
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
        Base.metadata.create_all(model.meta.engine)
