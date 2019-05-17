#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Q1mi"
# Date: 2019-01-24

"""
订单页面
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from api import models
from utils.response import BaseResponse
from api.auth import LoginAuth
from api.permission import LoginRequire


class OrderListView(APIView):

    authentication_classes = [LoginAuth, ]
    permission_classes = [LoginRequire, ]

    def get(self, request, *args, **kwargs):
        res_obj = BaseResponse()
        order_queryset = models.Order.objects.filter(account=request.user).order_by("-date")
        order_list = []
        for order in order_queryset:
            order_info = {
                "order_number": order.order_number,
                "date": order.date.strftime("%Y-%m-%d %H:%M:%S"),
                "status": order.get_status_display(),
                "actual_amount": order.actual_amount,
                "order_detail_list": [{
                    'course_name': detail.obj.content_object.name,
                    "origin_price": detail.original_price,
                    "price": detail.price,
                    "valid_period_display": detail.valid_period_display
                } for detail in order.orderdetail_set.all()]
            }
            order_list.append(order_info)
        res_obj.data = order_list
        return Response(res_obj.dict)
