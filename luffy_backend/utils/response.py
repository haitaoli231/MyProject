#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Q1mi"
# Date: 2019-01-17


class BaseResponse(object):
    def __init__(self):
        self.code = 0
        self.msg = ""
        self.data = None

    @property
    def dict(self):
        return self.__dict__
