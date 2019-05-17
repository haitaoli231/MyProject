#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Q1mi"
# Date: 2019-01-19

from rest_framework.filters import BaseFilterBackend
import logging
logger = logging.getLogger(__name__)


class CourseFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        # 过滤
        category_id = str(request.query_params.get('category', ''))
        logger.debug(category_id)
        if category_id and category_id is not '0' and category_id.isdigit():
            logger.debug(queryset)
            logger.debug('filter by category_id: {}'.format(category_id))
            queryset = queryset.filter(course_category_id=category_id)
            logger.debug(queryset)
        return queryset
