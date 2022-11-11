# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-ckanpackager
# Created by the Natural History Museum in London, UK

from ckan.plugins import interfaces


class ICkanPackager(interfaces.Interface):
    """
    
    """

    def before_package_request(
        self, resource_id, package_id, packager_url, request_params
    ):
        """
        Allows modification of the packager url and request parameters right before the
        request is sent to the ckanpackager backend. Must return both as a tuple.

        :param resource_id: the resource id of the resource that is about to be packaged
        :param package_id: the package id of the resource that is about to be packaged
        :param packager_url: the url that the request will be sent to
        :param request_params: the request parameters that will be sent to the
        ckanpackager
        :returns: a tuple of the url and the params
        """
        return packager_url, request_params
