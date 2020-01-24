# !/usr/bin/env python1
# encoding: utf-8
#
# This file is part of ckanext-ckanpackager
# Created by the Natural History Museum in London, UK
from ckan.model import meta, DomainObject
from sqlalchemy import Column, DateTime, Integer, func, Table, UnicodeText

ckanpackager_stats_table = Table(
    u'ckanpackager_stats',
    meta.metadata,
    Column(u'id', Integer, primary_key=True),
    # the current timestamp
    Column(u'inserted_on', DateTime, default=func.now()),
    Column(u'count', Integer),
    Column(u'resource_id', UnicodeText),
)


class CKANPackagerStat(DomainObject):
    '''
    Object for a datastore download row.
    '''
    pass


meta.mapper(CKANPackagerStat, ckanpackager_stats_table)
