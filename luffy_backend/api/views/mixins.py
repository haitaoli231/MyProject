#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Q1mi"
# Date: 2019-01-19
from utils.response import BaseResponse
from rest_framework.response import Response


class MyListViewMixin(object):

    def get_serializer_data(self):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        return data

    def get_my_response(self):
        res_obj = BaseResponse()
        res_obj.data = self.get_serializer_data()
        return Response(res_obj.dict)


class MyRetrieveViewMixin(object):

    def get_serializer_data(self):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return serializer.data

    def get_my_response(self):
        res_obj = BaseResponse()
        res_obj.data = self.get_serializer_data()
        return Response(res_obj.dict)