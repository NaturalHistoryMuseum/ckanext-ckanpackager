import json
import urllib
import urllib2
import ckan.plugins.toolkit as t
from ckan.lib.helpers import flash_error, flash_success
from ckanext.ckanpackager.plugin import config
from ckanext.ckanpackager.lib.utils import is_datastore_resource, url_for_resource, NotADatastoreResource, redirect_to

_ = t._


class CkanPackagerController(t.BaseController):

    def _setup_request(self, package_id=None, resource_id=None):
        """ Prepare generic values for a request """
        self.package_id = package_id
        self.resource_id = resource_id
        if 'destination' in t.request.params:
            self.destination = t.request.params['destination']
        else:
            self.destination = url_for_resource(self.package_id, self.resource_id)

    def _validate_request(self):
        """Validate the current request, and raise exceptions on errors"""
        # Validate resource
        try:
            if not is_datastore_resource(self.resource_id):
                raise NotADatastoreResource(self.resource_id)
        except t.ObjectNotFound:
            t.abort(404, _('Resource not found'))
        # Validate anonymous access and email parameters
        if 'anon' in t.request.params:
            flash_error(_("You must be logged on or have javascript enabled to use this functionality."))
            redirect_to(self.destination)
        if t.c.user and 'email' in t.request.params:
            flash_error(_("Parameter mismatch. Please reload the page and try again."))
            redirect_to(self.destination)
        if not t.c.user and 'email' not in t.request.params:
            flash_error(_("Please reload the page and try again."))
            redirect_to(self.destination)

    def _parse_filters(self, filters):
        """ Parse filters into JSON dictionary

        FIXME: Is there a CKAN API for this? The format changed with recent versions of CKAN, should we check for
               version?

        @param filters: String describing the filters
        @return: Dictionary of name to list of values
        """
        filters = {}
        for f in t.request.params['filters'].split('|'):
            try:
                (name, value) = f.split(':')
                if name in filters:
                    filters[name].append(value)
                else:
                    filters[name] = [value]
            except ValueError:
                pass
        return filters

    def package_resource(self, package_id, resource_id):
        """Action called to package a resource

        @param resource_id: The id of the resource
        """
        self._setup_request(package_id=package_id, resource_id=resource_id)
        self._validate_request()
        if t.c.user:
            email = t.c.userobj.email
        else:
            email = t.request.params['email']

        # Prepare the request
        # FIXME: Add user api key?
        request_params = {
            'api_url':  config['datastore_api'] + '/datastore_search',
            'secret': config['secret'],
            'resource_id': resource_id,
            'email': email
        }
        for option in ['filters', 'q', 'limit', 'offset']:
            if option in t.request.params:
                if option == 'filters':
                    request_params['filters'] = json.dumps(self._parse_filters(t.request.params['filters']))
                else:
                    request_params[option] = t.request.params[option]
        try:
            request = urllib2.Request(config['url'])
            response = urllib2.urlopen(request, urllib.urlencode(request_params))
        except urllib2.URLError as e:
            # FIXME: Log error
            flash_error(_("Failed to contact the ckanpackager service"))
            redirect_to(self.destination)
        if response.code != 200:
            response.close()
            # FIXME: Log error
            flash_error(_("Failed to contact the ckanpackager service"))
            redirect_to(self.destination)
        # Read response and return.
        try:
            data = response.read()
            result = json.loads(data)
        except ValueError:
            # FIXME: Log error
            flash_error(_("Could not parse response from ckanpackager service"))
            redirect_to(self.destination)
        finally:
            response.close()
        if 'message' in result:
            flash_success(result['message'])
        else:
            flash_success(_("Request successfully posted. The resource should be emailed to you shortly"))
        redirect_to(self.destination)
