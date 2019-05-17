#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Q1mi"
# Date: 2019-01-16

from rest_framework.generics import ListAPIView, RetrieveAPIView
from api import models
from api.serializers.course import CourseModelSerializer, CourseDetailModelSerializer, CourseCategoryModelSerializer
from rest_framework.response import Response
from api.filters.course import CourseFilter
from api.views.mixins import MyListViewMixin, MyRetrieveViewMixin
from utils.response import BaseResponse
from api.auth import LoginAuth

import logging
logger = logging.getLogger(__name__)


# 课程
class CourseListView(ListAPIView, MyListViewMixin):

    queryset = models.Course.objects.all()
    serializer_class = CourseModelSerializer
    filter_backends = (CourseFilter, )

    def get(self, request, *args, **kwargs):
        res_obj = BaseResponse()
        data = self.get_serializer_data()
        # 排序(是对序列化之后的数据排序而不是对queryset排序)
        ordering = request.query_params.get('ordering', '')
        if ordering:
            ordering_key, reverse = (ordering[1:], True) if ordering.startswith('-') else (ordering, False)
            data = sorted(data, key=lambda item: float(item.get(ordering_key, 0)), reverse=reverse)
            logger.debug(data)
        res_obj.data = data
        return Response(res_obj.dict)


# 课程详情
class CourseDetailView(RetrieveAPIView, MyRetrieveViewMixin):
    queryset = models.CourseDetail.objects.all()
    serializer_class = CourseDetailModelSerializer
    authentication_classes = [LoginAuth, ]

    def get(self, request, *args, **kwargs):
        return self.get_my_response()


# 课程分类
class CourseCategoryView(ListAPIView, MyListViewMixin):
    queryset = models.CourseCategory.objects.all()
    serializer_class = CourseCategoryModelSerializer

    def get(self, request, *args, **kwargs):
        return self.get_my_response()
