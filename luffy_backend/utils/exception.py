#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Q1mi"
# Date: 2019-01-23


class LuffyException(Exception):

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg
