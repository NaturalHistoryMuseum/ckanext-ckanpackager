# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-ckanpackager
# Created by the Natural History Museum in London, UK

import json
import urllib
import urllib2

from ckanext.ckanpackager.interfaces import ICkanPackager
from ckanext.ckanpackager.lib.utils import (is_downloadable_resource, redirect_to,
                                            url_for_resource_page)
from ckanext.ckanpackager.model.stat import CKANPackagerStat
from ckanext.ckanpackager.plugin import config

import ckan.model as model
import ckan.plugins.toolkit as t
from ckan.lib.helpers import flash_error, flash_success
from ckan.plugins import PluginImplementations

_ = t._


class PackagerControllerError(Exception):
    ''' '''
    pass


class CkanPackagerController(t.BaseController):
    ''' '''
    def _setup_request(self, package_id=None, resource_id=None):
        '''Prepare generic values for a request

        :param package_id: The package id (request parameter) (Default value = None)
        :param resource_id: The resource id (Request parameter) (Default value = None)

        '''
        self.package_id = package_id
        self.resource_id = resource_id
        if u'destination' in t.request.params:
            self.destination = t.request.params[u'destination']
        else:
            self.destination = url_for_resource_page(self.package_id, self.resource_id)

    def _validate_request(self):
        '''Validate the current request, and raise exceptions on errors'''
        # Validate resource
        try:
            if not is_downloadable_resource(self.resource_id):
                raise PackagerControllerError(_(u'This resource cannot be downloaded'))
        except t.ObjectNotFound:
            raise PackagerControllerError(u'Resource not found')

        # Validate anonymous access and email parameters
        if u'anon' in t.request.params:
            raise PackagerControllerError(_(
                u'You must be logged on or have javascript enabled to use this '
                u'functionality.'))
        if t.c.user and u'email' in t.request.params:
            raise PackagerControllerError(
                _(u'Parameter mismatch. Please reload the page and try again.'))
        if not t.c.user and u'email' not in t.request.params:
            raise PackagerControllerError(_(u'Please reload the page and try again.'))

    def package_resource(self, package_id, resource_id):
        '''Action called to package a resource

        :param package_id: The package id
        :param resource_id: The resource id

        '''
        try:
            self._setup_request(package_id=package_id, resource_id=resource_id)
            self._validate_request()

            if t.c.user:
                email = t.c.userobj.email
            else:
                email = t.request.params[u'email']

            packager_url, request_params = self._prepare_packager_parameters(email,
                                                                             resource_id,
                                                                             t.request.params)

            # cycle through any implementors
            for plugin in PluginImplementations(ICkanPackager):
                packager_url, request_params = plugin.before_package_request(resource_id,
                                                                             package_id,
                                                                             packager_url,
                                                                             request_params)

            result = self._send_packager_request(packager_url, request_params)
            if u'message' in result:
                flash_success(result[u'message'])
            else:
                flash_success(_(
                    u'Request successfully posted. The resource should be emailed to '
                    u'you shortly'))
        except PackagerControllerError as e:
            flash_error(e.message)
        else:
            # Create new download object
            stat = CKANPackagerStat(
                resource_id=request_params[u'resource_id'],
                count=request_params.get(u'limit', 0),
                )
            model.Session.add(stat)
            model.Session.commit()

        redirect_to(self.destination)

    def _prepare_packager_parameters(self, email, resource_id, params):
        '''Prepare the parameters for the ckanpackager service for the current request

        :param resource_id: The resource id
        :param params: A dictionary of parameters
        :param email: 
        :returns: A tuple defining an URL and a dictionary of parameters

        '''
        packager_url = config[u'url']
        request_params = {
            u'secret': config[u'secret'],
            u'resource_id': resource_id,
            u'email': email,
            # default to csv format, this can be overridden in the params
            u'format': u'csv',
            }

        resource = t.get_action(u'resource_show')(None, {
            u'id': resource_id
            })
        if resource.get(u'datastore_active', False):
            if resource.get(u'format', u'').lower() == u'dwc':
                packager_url += '/package_dwc_archive'
            else:
                packager_url += '/package_datastore'
            request_params[u'api_url'] = config[u'datastore_api'] + '/datastore_search'
            for option in [u'filters', u'q', u'limit', u'offset', u'resource_url',
                           u'sort', u'format']:
                if option in params:
                    if option == u'filters':
                        request_params[u'filters'] = json.dumps(
                            self._parse_filters(params[u'filters']))
                    else:
                        request_params[option] = params[option]
            if u'limit' not in request_params:
                # It's best to actually add a limit, so the packager knows how to
                # prioritize the request.
                prep_req = {
                    u'limit': 1,  # Using 0 does not return the total
                    u'resource_id': request_params[u'resource_id']
                    }
                if u'filters' in request_params:
                    prep_req[u'filters'] = request_params[u'filters']
                if u'q' in request_params:
                    prep_req[u'q'] = request_params[u'q']

                # BUGFIX: BS timeout on download request
                # Try and use the solr search if it exists
                try:
                    search_action = t.get_action(u'datastore_solr_search')
                # Otherwise fallback to default
                except KeyError:
                    search_action = t.get_action(u'datastore_search')

                result = search_action({}, prep_req)

                request_params[u'limit'] = result[u'total'] - request_params.get(
                    u'offset', 0)
        elif resource.get(u'url', False):
            packager_url += '/package_url'
            request_params[u'resource_url'] = resource.get(u'url')

        return packager_url, request_params

    def _send_packager_request(self, packager_url, request_params):
        '''Send the request to the ckanpackager service

        :param packager_url: The ckanpackager service URL
        @request_params: The parameters to send
        :param request_params: 

        '''
        # Send request
        try:
            request = urllib2.Request(packager_url)
            response = urllib2.urlopen(request, urllib.urlencode(request_params))
        except urllib2.URLError as e:
            raise PackagerControllerError(
                _(u'Failed to contact the ckanpackager service'))
        if response.code != 200:
            response.close()
            raise PackagerControllerError(
                _(u'Failed to contact the ckanpackager service'))

        # Read response and return.
        try:
            data = response.read()
            result = json.loads(data)
        except ValueError:
            raise PackagerControllerError(
                _(u'Could not parse response from ckanpackager service'))
        finally:
            response.close()
        return result

    def _parse_filters(self, filters):
        '''Parse filters into JSON dictionary
        
        TODO: Is there a CKAN API for this? The format changed with recent versions of
        CKAN, should we check for
               version?

        :param filters: String describing the filters
        :returns: Dictionary of name to list of values

        '''
        result = {}
        for f in filters.split(u'|'):
            try:
                (name, value) = f.split(u':')
                if name in result:
                    result[name].append(value)
                else:
                    result[name] = [value]
            except ValueError:
                pass
        return result
