#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Q1mi"
# Date: 2019-01-22

"""
结算

1. 购物车 勾选课程及价格策略 去结算
2. 点击课程的立即购买
"""

from rest_framework.views import APIView
from utils.response import BaseResponse
from rest_framework.response import Response
from api.auth import LoginAuth
from api.permission import LoginRequire
from api import models
import logging
import datetime
import django_redis
import json

cache = django_redis.get_redis_connection()
logger = logging.getLogger(__name__)


class CheckOutView(APIView):
    authentication_classes = [LoginAuth, ]
    permission_classes = [LoginRequire, ]

    def _get_coupon_list(self, request, course_id=None):

        now = datetime.datetime.utcnow()
        coupon_record_list = models.CouponRecord.objects.filter(
            account=request.user,
            status=0,
            coupon__valid_begin_date__lte=now,
            coupon__valid_end_date__gt=now,
            coupon__content_type__model='course',
            coupon__object_id=course_id
        )
        print('*' * 120)
        print(coupon_record_list)
        print('*' * 120)
        coupon_list = []
        for coupon_record in coupon_record_list:
            coupon_list.append({
                "pk": coupon_record.pk,
                "name": coupon_record.coupon.name,
                "coupon_type": coupon_record.coupon.get_coupon_type_display(),
                "money_equivalent_value": coupon_record.coupon.money_equivalent_value,
                "off_percent": coupon_record.coupon.off_percent,
                "minimum_consume": coupon_record.coupon.minimum_consume,
            })
        return coupon_list

    def post(self, request, *args, **kwargs):
        """
        获取用户提交的课程id和价格策略id
        接收的数据类型：
        [
            {course_id: 1, price_policy_id: 6},
            {course_id: 2, price_policy_id: 3},
        ]

        """
        user_id = request.user.id

        checkout_list = []
        res_obj = BaseResponse()
        course_list = request.data.get('course_list')
        print(course_list, type(course_list))

        for course_dict in course_list:
            course_id = course_dict.get('course_id')
            price_policy_id = course_dict.get('price_policy_id')
            # 先判断参数齐不齐
            if not (course_id and price_policy_id):
                logger.warning('post checkout without course_id and price_policy_id.')
                res_obj.code = 3001
                res_obj.msg = '无效的参数'
                return Response(res_obj.dict)
            # 校验课程id和价格策略id是否合法
            course_obj = models.Course.objects.filter(id=course_id).first()
            if not course_obj:
                res_obj.code = 3002
                res_obj.msg = '无效的课程id'
                logger.debug('post checkout with invalid course_id')
                return Response(res_obj.dict)
            price_policy_obj = models.PricePolicy.objects.filter(id=price_policy_id).first()
            # 拿到该课程所有的价格策略
            price_policy_list = course_obj.price_policy.all()
            if not (price_policy_obj and price_policy_obj in price_policy_list):
                res_obj.code = 3003
                res_obj.msg = '无效的价格策略id'
                logger.debug('post checkout with invalid price_policy_id')
                return Response(res_obj.dict)
            price_policy_dict = {}
            for price_policy in price_policy_list:
                price_policy_dict[str(price_policy.pk)] = {
                    "price": price_policy.price,
                    "valid_period": price_policy.valid_period,
                    "valid_period_text": price_policy.get_valid_period_display(),
                    "selected": price_policy.pk == price_policy_id
                }
            # 构造数据 结算页面的数据结构
            course_info = {
                "id": course_id,
                "name": course_obj.name,
                "course_img": course_obj.course_img,
                "relate_price_policy": price_policy_dict,
                "default_price": price_policy_obj.price,
                "default_price_period": price_policy_obj.valid_period,
                "default_price_policy_id": price_policy_obj.pk
            }
            # 查询当前用户拥有未使用的，在有效期的且与当前课程相关的优惠券
            coupon_list = self._get_coupon_list(request, course_id)
            course_info['course_coupon'] = coupon_list
            # 把当前课程加到结算列表中
            checkout_list.append(course_info)
        # 获取当前用户的通用优惠券
        common_coupon_list = self._get_coupon_list(request)
        # 先清空已有的结算信息，以最后一次结算信息为准
        cache.delete(f'COMMON_COUPON_LIST_{user_id}', f'CHECKOUT_LIST_{user_id}')
        # 再存缓存
        cache.set(f'CHECKOUT_LIST_{user_id}', json.dumps(checkout_list))
        cache.set(f'COMMON_COUPON_LIST_{user_id}', json.dumps(common_coupon_list))
        print('=' * 120)
        print(checkout_list)
        print(common_coupon_list)
        print('=' * 120)
        res_obj.msg = '提交结算数据成功'
        return Response(res_obj.dict)

    def get(self, request, *args, **kwargs):
        """返回结算中心页面"""
        res_obj = BaseResponse()
        user_id = request.user.id
        checkout_list_value = cache.get(f'CHECKOUT_LIST_{user_id}')
        if not checkout_list_value:
            res_obj.code = 3004
            res_obj.msg = '暂无结算信息'
            logger.warning('no checkout info.')
            return Response(res_obj.dict)
        checkout_list = json.loads(checkout_list_value)

        # 获取通用优惠券
        common_coupon_value = cache.get(f'COMMON_COUPON_LIST_{user_id}')
        common_coupon_value = json.loads(common_coupon_value) if common_coupon_value else []

        res_obj.data = {
            'checkout_list': checkout_list,
            'common_coupon_list': common_coupon_value
        }
        return Response(res_obj.dict)
