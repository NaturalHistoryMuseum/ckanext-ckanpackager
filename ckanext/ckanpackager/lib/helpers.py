# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-ckanpackager
# Created by the Natural History Museum in London, UK

from ckan.plugins import toolkit


def should_show_format_options(resource_id):
    '''
    Determines whether the format options should be shown for a given resource id.

    :param resource_id: the resource's id
    :returns: True if they should be shown, False if not
    '''
    resource = toolkit.get_action(u'resource_show')({}, dict(id=resource_id))
    # currently we just predicate on whether the resource is in the datastore or not
    return resource.get(u'datastore_active', False)
