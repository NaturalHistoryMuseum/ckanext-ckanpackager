# !/usr/bin/env python1
# encoding: utf-8
#
# This file is part of ckanext-ckanpackager
# Created by the Natural History Museum in London, UK


from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CKANPackagerStat(Base):
    '''Table for holding resource stats'''
    __tablename__ = u'ckanpackager_stats'

    id = Column(Integer, primary_key=True)
    inserted_on = Column(DateTime,
                         default=func.now())  # the current timestamp
    count = Column(Integer)
    resource_id = Column(String)
