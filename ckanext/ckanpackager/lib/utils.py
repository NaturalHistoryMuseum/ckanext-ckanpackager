# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-ckanpackager
# Created by the Natural History Museum in London, UK
import json
from collections import defaultdict

import requests
from ckan.plugins import toolkit

from ..logic.action import ALLOWED_PARAMS


def is_downloadable_resource(resource_id):
    '''
    Returns True if the resource can be downloaded - either because it is in the datastore or we
    have a URL link to it.

    :param resource_id: the resource id
    :raises ckan.plugins.toolkit.ObjectNotFound: if the resource does not exist
    :returns: True or False
    '''
    resource = toolkit.get_action('resource_show')({}, {'id': resource_id})
    return resource.get('datastore_active', False) or resource.get('url', False)


def url_for_package_resource(
    package_id, resource_id, use_request=True, extra_filters=None
):
    """
    Given a resource_id, return the URL for packaging that resource. Will return an
    empty URL if the resource exists but is not downloadable.

    :param package_id: the package id
    :param resource_id: the resource id
    :param use_request: if True (default) include the filters of the current request
    :param extra_filters: extra filters (on top of those in the request URL) to add to the link
    :raises ckan.plugins.toolkit.ObjectNotFound: if the resource does not exist
    :return: the URL to request packaging the resource
    """
    if use_request:
        params = dict(toolkit.request.view_args)
    else:
        params = {}

    resource = toolkit.get_action('resource_show')({}, {'id': resource_id})
    if not resource.get('datastore_active', False):
        if resource.get('url', False):
            params['resource_url'] = resource.get('url')
        else:
            return ''

    filters = []
    if 'filters' in params:
        filters = params['filters'].split('|')
    if extra_filters:
        filters += [f'{k}:{v}' for k, v in extra_filters.items()]
    if filters:
        params['filters'] = '|'.join(filters)

    params['resource_id'] = resource_id
    params['package_id'] = package_id
    params['destination'] = toolkit.request.url

    return toolkit.url_for('ckanpackager.package_resource', **params)


def get_redirect_url(package_id, resource_id):
    """
    Determine the URL to redirect the requester to after making the packager request.

    :param package_id: the package id
    :param resource_id: the resource id
    """
    if 'destination' in toolkit.request.params:
        return toolkit.request.params['destination']
    else:
        return toolkit.url_for('dataset.read', id=package_id, resource_id=resource_id)


def validate_request(resource_id):
    """
    Validate the current request, and raise exceptions on errors.

    :param resource_id: the resource id
    """
    # validate resource
    try:
        if not is_downloadable_resource(resource_id):
            raise PackagerControllerError.build('This resource cannot be downloaded')
    except toolkit.ObjectNotFound:
        raise PackagerControllerError.build('Resource not found')

    # check that we have an email address
    if 'email' not in toolkit.request.params and not toolkit.c.user:
        raise PackagerControllerError.build(
            'An email must be provided or you must be logged in'
        )


def prepare_packager_parameters(resource_id, params):
    """
    Prepare the URL and parameters for the ckanpackager service from the params.

    :param resource_id: the resource id
    :param params: a dictionary of parameters
    :return: a tuple defining an URL and a dictionary of parameters
    """
    resource = toolkit.get_action('resource_show')(None, {'id': resource_id})
    packager_url = toolkit.config.get('ckanpackager.url')
    request_params = {
        'secret': toolkit.config.get('ckanpackager.secret'),
        'resource_id': resource_id,
        # the request has been validated which means there's either an email param or a user
        # available. We prioritise the email param.
        'email': toolkit.request.params.get(
            'email', getattr(toolkit.c.userobj, 'email', None)
        ),
        # default to csv format, this can be overridden in the params
        'format': 'csv',
    }

    # if there is a logged-in user, send over their apikey so that the packager can access resources
    # that require authentication (i.e. ones in private datasets)
    if toolkit.c.userobj and toolkit.c.userobj.apikey:
        request_params['key'] = toolkit.c.userobj.apikey

    if resource.get('datastore_active', False):
        # dwc resources get special treatment
        if resource.get('format', '').lower() == 'dwc':
            packager_url += '/package_dwc_archive'
        else:
            packager_url += '/package_datastore'

        request_params[
            'api_url'
        ] = f'{toolkit.config["datastore_api"]}/datastore_search'

        # process a list of options we allow
        for option in [
            'filters',
            'q',
            'limit',
            'offset',
            'resource_url',
            'sort',
            'format',
        ]:
            if option in params:
                if option == 'filters':
                    request_params['filters'] = json.dumps(
                        parse_filters(params['filters'])
                    )
                else:
                    request_params[option] = params[option]

        if 'limit' not in request_params:
            # it's best to actually add a limit, so the packager knows how to prioritize the
            # request. This is also used by the calling route which creates a stats object off the
            # back of this limit
            prep_req = {
                # TODO: pretty sure it does return a total but needs checking...
                'limit': 1,  # using 0 does not return the total
                'resource_id': request_params['resource_id'],
            }
            if 'filters' in request_params:
                prep_req['filters'] = request_params['filters']
            if 'q' in request_params:
                prep_req['q'] = request_params['q']
            # run the datastore_search action to get the total
            result = toolkit.get_action('datastore_search')({}, prep_req)
            request_params['limit'] = result['total'] - request_params.get('offset', 0)
    elif resource.get('url', False):
        packager_url += '/package_url'
        request_params['resource_url'] = resource.get('url')

    return packager_url, request_params


def send_packager_request(packager_url, params):
    """
    Send the request to the ckanpackager service.

    :param packager_url: the ckanpackager service URL
    :param params: the parameters to send
    """
    try:
        r = requests.post(packager_url, params)
        r.raise_for_status()
    except Exception:
        raise PackagerControllerError.build(
            'Failed to contact the ckanpackager service'
        )

    try:
        return r.json()
    except Exception:
        raise PackagerControllerError.build(
            'Could not parse response from ckanpackager service'
        )


def parse_filters(filters):
    """
    Parse datastore URL filters into JSON dictionary.

    :param filters: String describing the filters
    :return: Dictionary of name to list of values
    """
    # TODO: is there a CKAN API for this? The format changed with recent versions of CKAN, should we
    #       check for version?
    result = defaultdict(list)
    for f in filters.split('|'):
        try:
            name, value = f.split(':', 1)
            result[name].append(value)
        except ValueError:
            pass
    return result


def get_options_from_request():
    """
    Filters the request parameters passed, sets defaults for offset and limit and
    returns as a dict.

    :return: a dict of options
    """
    # we'll fill out the extra parameters using the query string parameters, however we want to
    # filter to ensure we only pass parameters we want to allow
    params = {
        key: value
        for key, value in toolkit.request.params.items()
        if key in ALLOWED_PARAMS
    }
    params.setdefault('limit', 100)
    params.setdefault('offset', 0)
    return params


class PackagerControllerError(Exception):
    pass

    @classmethod
    def build(cls, message):
        return cls(toolkit._(message))
