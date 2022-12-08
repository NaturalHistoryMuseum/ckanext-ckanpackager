# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-ckanpackager
# Created by the Natural History Museum in London, UK

import os
import requests
from ckan.model import Session
from ckan.plugins import PluginImplementations, toolkit
from flask import Blueprint, jsonify

from ..interfaces import ICkanPackager
from ..model.stat import CKANPackagerStat
from ..lib.utils import (
    get_redirect_url,
    validate_request,
    prepare_packager_parameters,
    send_packager_request,
    PackagerControllerError,
    get_options_from_request,
)

blueprint = Blueprint(name='ckanpackager', import_name=__name__)

success_message = (
    'Request successfully posted. The resource should be emailed to you shortly.'
)


@blueprint.route('/dataset/<package_id>/resource/<resource_id>/package')
def package_resource(package_id, resource_id):
    """
    Route which when called queues a download and then redirects the caller to either
    the requested destination or the resource home page.

    :param package_id: the package id
    :param resource_id: the resource id
    """
    destination = get_redirect_url(package_id=package_id, resource_id=resource_id)
    try:
        validate_request(resource_id)
        packager_url, params = prepare_packager_parameters(
            resource_id, toolkit.request.params
        )

        # cycle through any implementors
        for plugin in PluginImplementations(ICkanPackager):
            packager_url, params = plugin.before_package_request(
                resource_id, package_id, packager_url, params
            )

        result = send_packager_request(packager_url, params)
        toolkit.h.flash_success(result.get('message', success_message))
    except PackagerControllerError as e:
        toolkit.h.flash_error(str(e))
    else:
        # create new download stats object
        stat = CKANPackagerStat(
            resource_id=params['resource_id'],
            # TODO: do this in a more robust way? This currently relies on
            #       prepare_packager_parameters adding a limit to the params
            count=params.get('limit', 0),
        )
        Session.add(stat)
        Session.commit()

    return toolkit.redirect_to(destination)


@blueprint.route('/stats/ckanpackager')
def get_stats():
    """
    Retrieves the stats from the ckanpackager's statistics/requests endpoint, passing
    any allowed request parameters along too. The response is returned as JSON.

    :return: the JSON returned by the ckanpackager
    """
    # create the url to post to
    url = '/'.join(toolkit.config.get('ckanpackager.url'), 'statistics', 'requests')
    # this is the data we're going to pass in the request, it has to have the secret in it
    data = {'secret': toolkit.config.get('ckanpackager.secret')}
    # update the data dict with the options from the request parameters
    data.update(get_options_from_request())
    # make the request
    response = requests.post(url, data=data)
    # and return the data
    return jsonify(response.json())
