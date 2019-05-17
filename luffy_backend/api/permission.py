#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Q1mi"
# Date: 2019-01-20

from rest_framework.permissions import BasePermission


class LoginRequire(BasePermission):
    """只判断是否登录，有token就是登录过"""
    def has_permission(self, request, view):
        if request.user:
            return True
        else:
            return False
