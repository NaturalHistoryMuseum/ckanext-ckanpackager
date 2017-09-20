#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import sys
import os
import ckan.model as model
from ckan.model.resource import Resource
from sqlalchemy import Column, Integer, DateTime, String, func
# from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CKANPackagerStat(Base):
    """
    Table for holding resource stats
    """
    __tablename__ = 'ckanpackager_stats'

    id = Column(Integer, primary_key=True)
    inserted_on = Column(DateTime, default=func.now())  # the current timestamp
    count = Column(Integer)
    resource_id = Column(String)
