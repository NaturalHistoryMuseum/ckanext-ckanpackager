# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-ckanpackager
# Created by the Natural History Museum in London, UK

import os
import requests
from ckanext.ckanpackager.logic.action import ALLOWED_PARAMS
from flask import Blueprint, jsonify

from ckan.plugins import toolkit

blueprint = Blueprint(name=u'ckanpackager-stats', import_name=__name__)


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
    data.update(_get_options_from_request())
    # make the request
    response = requests.post(url, data=data)
    # and return the data
    return jsonify(response.json())


def _get_options_from_request():
    '''
    Filters the request parameters passed, sets defaults for offset and limit and returns as a dict.

    :return: a dict of options
    '''

    # we'll fill out the extra parameters using the query string parameters, however we want to
    # filter to ensure we only pass parameters we want to allow
    params = {key: value for key, value in toolkit.request.params.items() if key in ALLOWED_PARAMS}
    params.setdefault(u'limit', 100)
    params.setdefault(u'offset', 0)
    return params
