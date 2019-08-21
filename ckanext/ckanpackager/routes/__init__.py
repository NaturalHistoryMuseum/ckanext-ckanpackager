# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-ckanpackager
# Created by the Natural History Museum in London, UK

from . import packager, stats

blueprints = [packager.blueprint, stats.blueprint]
