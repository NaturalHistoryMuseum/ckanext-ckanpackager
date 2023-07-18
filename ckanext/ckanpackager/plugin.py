# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-ckanpackager
# Created by the Natural History Museum in London, UK

from ckan.plugins import SingletonPlugin, implements, interfaces

from ckanext.ckanpackager import cli


class CkanPackagerPlugin(SingletonPlugin):
    implements(interfaces.IClick)

    # IClick
    def get_commands(self):
        return cli.get_commands()
