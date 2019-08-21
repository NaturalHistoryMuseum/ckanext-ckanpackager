# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-ckanpackager
# Created by the Natural History Museum in London, UK

import os
import requests
from ckanext.ckanpackager.interfaces import ICkanPackager
from ckanext.ckanpackager.model.stat import CKANPackagerStat
from flask import Blueprint, jsonify

from ckan.model import Session
from ckan.plugins import PluginImplementations, toolkit
from . import _helpers

blueprint = Blueprint(name=u'ckanpackager', import_name=__name__)


@blueprint.route('/dataset/<package_id>/resource/<resource_id>/package')
def package_resource(package_id, resource_id):
    '''Action called to package a resource.'''
    try:
        destination = _helpers.setup_request(package_id=package_id, resource_id=resource_id)
        _helpers.validate_request(resource_id)

        if toolkit.c.user:
            email = toolkit.c.userobj.email
        else:
            email = toolkit.request.params[u'email']

        packager_url, request_params = _helpers.prepare_packager_parameters(email,
                                                                            resource_id,
                                                                            toolkit.request.params)

        # cycle through any implementors
        for plugin in PluginImplementations(ICkanPackager):
            packager_url, request_params = plugin.before_package_request(resource_id,
                                                                         package_id,
                                                                         packager_url,
                                                                         request_params)

        result = _helpers.send_packager_request(packager_url, request_params)
        if u'message' in result:
            toolkit.h.flash_success(result[u'message'])
        else:
            toolkit.h.flash_success(toolkit._(
                u'Request successfully posted. The resource should be emailed to '
                u'you shortly.'))
    except _helpers.PackagerControllerError as e:
        toolkit.h.flash_error(e.message)
    else:
        # Create new download object
        stat = CKANPackagerStat(
            resource_id=request_params[u'resource_id'],
            count=request_params.get(u'limit', 0),
            )
        Session.add(stat)
        Session.commit()

    return toolkit.redirect_to(destination)


@blueprint.route('/stats/ckanpackager')
def get_stats():
    '''
    Retrieves the stats from the ckanpackager's statistics/requests endpoint, passing any
    allowed request parameters along too. The response is returned as JSON.

    :return: the JSON returned by the ckanpackager
    '''
    # create the url to post to
    url = os.path.join(toolkit.config.get(u'ckanext.ckanpackager.url'), u'statistics', u'requests')
    # this is the data we're going to pass in the request, it has to have the secret in it
    data = {
        u'secret': toolkit.config.get(u'ckanext.ckanpackager.secret')
        }
    # update the data dict with the options from the request parameters
    data.update(_helpers.get_options_from_request())
    # make the request
    response = requests.post(url, data=data)
    # and return the data
    return jsonify(response.json())
