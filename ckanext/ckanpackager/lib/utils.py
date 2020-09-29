# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-ckanpackager
# Created by the Natural History Museum in London, UK
import json
import requests
from ckan.plugins import toolkit
from collections import defaultdict

from ..logic.action import ALLOWED_PARAMS


def is_downloadable_resource(resource_id):
    '''
    Returns True if the resource can be downloaded - either because it is in the datastore or we
    have a URL link to it.

    :param resource_id: the resource id
    :raises ckan.plugins.toolkit.ObjectNotFound: if the resource does not exist
    :returns: True or False
    '''
    resource = toolkit.get_action(u'resource_show')({}, {u'id': resource_id})
    return resource.get(u'datastore_active', False) or resource.get(u'url', False)


def url_for_package_resource(package_id, resource_id, anon=True, use_request=True,
                             extra_filters=None):
    '''
    Given a resource_id, return the URL for packaging that resource. Will return an empty URL if the
    resource exists but is not downloadable.

    :param package_id: the package id
    :param resource_id: the resource id
    :param anon: if True, will add 'anon=1' to the query string *if* this is an anonymous request
    :param use_request: if True (default) include the filters of the current request
    :param extra_filters: extra filters (on top of those in the request URL) to add to the link
    :raises ckan.plugins.toolkit.ObjectNotFound: if the resource does not exist
    :return: the URL to request packaging the resource
    '''
    if use_request:
        params = dict(toolkit.request.view_args)
    else:
        params = {}

    resource = toolkit.get_action(u'resource_show')({}, {u'id': resource_id})
    if not resource.get(u'datastore_active', False):
        if resource.get(u'url', False):
            params[u'resource_url'] = resource.get(u'url')
        else:
            return u''

    filters = []
    if u'filters' in params:
        filters = params[u'filters'].split(u'|')
    if extra_filters:
        filters += [u'%s:%s' % (k, v) for (k, v) in extra_filters.items()]
    if filters:
        params[u'filters'] = u'|'.join(filters)

    params[u'resource_id'] = resource_id
    params[u'package_id'] = package_id
    params[u'destination'] = toolkit.request.url
    if anon and not toolkit.c.user:
        params[u'anon'] = u'1'

    return toolkit.url_for(u'ckanpackager.package_resource', **params)


def get_redirect_url(package_id, resource_id):
    '''
    Determine the URL to redirect the requester to after making the packager request.

    :param package_id: the package id
    :param resource_id: the resource id
    '''
    if u'destination' in toolkit.request.params:
        return toolkit.request.params[u'destination']
    else:
        return toolkit.url_for(u'dataset.read', id=package_id, resource_id=resource_id)


def validate_request(resource_id):
    '''
    Validate the current request, and raise exceptions on errors.

    :param resource_id: the resource id
    '''
    # validate resource
    try:
        if not is_downloadable_resource(resource_id):
            raise PackagerControllerError.build(u'This resource cannot be downloaded')
    except toolkit.ObjectNotFound:
        raise PackagerControllerError.build(u'Resource not found')

    # validate anonymous access and email parameters
    if u'anon' in toolkit.request.params:
        # TODO: what the jamboree is this (what does anonymous access have to do with javascript?)
        raise PackagerControllerError.build(u'You must be logged on or have javascript enabled to'
                                            u'use this functionality.')

    # check that we have an email address
    if u'email' not in toolkit.request.params and not toolkit.c.user:
        raise PackagerControllerError.build(u'An email must be provided or you must be logged in')


def prepare_packager_parameters(resource_id, params):
    '''
    Prepare the URL and parameters for the ckanpackager service from the params.

    :param resource_id: the resource id
    :param params: a dictionary of parameters
    :return: a tuple defining an URL and a dictionary of parameters
    '''
    resource = toolkit.get_action(u'resource_show')(None, {u'id': resource_id})
    packager_url = toolkit.config.get(u'ckanpackager.url')
    request_params = {
        u'secret': toolkit.config.get(u'ckanpackager.secret'),
        u'resource_id': resource_id,
        # the request has been validated which means there's either an email param or a user
        # available. We prioritise the email param.
        u'email': toolkit.request.params.get(u'email', getattr(toolkit.c.userobj, u'email', None)),
        # default to csv format, this can be overridden in the params
        u'format': u'csv',
    }

    if resource.get(u'datastore_active', False):
        # dwc resources get special treatment
        if resource.get(u'format', u'').lower() == u'dwc':
            packager_url += u'/package_dwc_archive'
        else:
            packager_url += u'/package_datastore'

        request_params[u'api_url'] = toolkit.config[u'datastore_api'] + u'/datastore_search'

        # process a list of options we allow
        for option in [u'filters', u'q', u'limit', u'offset', u'resource_url', u'sort', u'format']:
            if option in params:
                if option == u'filters':
                    request_params[u'filters'] = json.dumps(parse_filters(params[u'filters']))
                else:
                    request_params[option] = params[option]

        if u'limit' not in request_params:
            # it's best to actually add a limit, so the packager knows how to prioritize the
            # request. This is also used by the calling route which creates a stats object off the
            # back of this limit
            prep_req = {
                # TODO: pretty sure it does return a total but needs checking...
                u'limit': 1,  # using 0 does not return the total
                u'resource_id': request_params[u'resource_id']
            }
            if u'filters' in request_params:
                prep_req[u'filters'] = request_params[u'filters']
            if u'q' in request_params:
                prep_req[u'q'] = request_params[u'q']
            # run the datastore_search action to get the total
            result = toolkit.get_action(u'datastore_search')({}, prep_req)
            request_params[u'limit'] = result[u'total'] - request_params.get(u'offset', 0)
    elif resource.get(u'url', False):
        packager_url += '/package_url'
        request_params[u'resource_url'] = resource.get(u'url')

    return packager_url, request_params


def send_packager_request(packager_url, params):
    '''
    Send the request to the ckanpackager service.

    :param packager_url: the ckanpackager service URL
    :param params: the parameters to send
    '''
    try:
        r = requests.post(packager_url, params)
        r.raise_for_status()
    except Exception:
        raise PackagerControllerError.build(u'Failed to contact the ckanpackager service')

    try:
        return r.json()
    except Exception:
        raise PackagerControllerError.build(u'Could not parse response from ckanpackager service')


def parse_filters(filters):
    '''
    Parse datastore URL filters into JSON dictionary.

    :param filters: String describing the filters
    :return: Dictionary of name to list of values
    '''
    # TODO: is there a CKAN API for this? The format changed with recent versions of CKAN, should we
    #       check for version?
    result = defaultdict(list)
    for f in filters.split(u'|'):
        try:
            name, value = f.split(u':', 1)
            result[name].append(value)
        except ValueError:
            pass
    return result


def get_options_from_request():
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


class PackagerControllerError(Exception):
    pass

    @classmethod
    def build(cls, message):
        return cls(toolkit._(message))
