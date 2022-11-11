# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-ckanpackager
# Created by the Natural History Museum in London, UK
from typing import List

from ckan.plugins import toolkit


def get_format_options(resource_id: str) -> List[str]:
    """
    Determines whether the format options should be shown for a given resource id.

    :param resource_id: the resource's id
    :returns: True if they should be shown, False if not
    """
    resource = toolkit.get_action('resource_show')({}, dict(id=resource_id))
    formats = []
    if resource.get('datastore_active', False):
        formats.extend(['CSV', 'TSV'])
        if resource.get('format', '').lower() != 'dwc':
            formats.append('XLSX')
    return formats
