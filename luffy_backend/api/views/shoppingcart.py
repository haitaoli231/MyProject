#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Q1mi"
# Date: 2019-01-21

"""
购物车
"""
from rest_framework.views import APIView
from api.auth import LoginAuth
from api.permission import LoginRequire
from api import models
from utils.response import BaseResponse
from rest_framework.response import Response
import django_redis
import json
import logging

logger = logging.getLogger(__name__)

CACHE = django_redis.get_redis_connection()


class ShoppingCartView(APIView):
    authentication_classes = [LoginAuth, ]
    permission_classes = [LoginRequire, ]

    def post(self, request, *args, **kwargs):
        res_obj = BaseResponse()
        """加入购物车操作"""
        # 1. 获取数据
        course_id = request.data.get('course_id')
        price_policy_id = request.data.get('price_policy_id')
        user_id = request.user.id
        # 2. 校验数据的合法性
        # 2.1 验证课程id是否合法
        course_obj = models.Course.objects.filter(id=course_id).first()
        if not course_obj:
            res_obj.code = 2001
            res_obj.msg = '课程id无效'
            return Response(res_obj.dict)
        # 2.2 验证价格策略id是否合法
        price_obj = course_obj.price_policy.all().filter(id=price_policy_id).first()
        if not price_obj:
            res_obj.code = 2002
            res_obj.msg = '价格策略无效'
            return Response(res_obj.dict)

        # 3. 获取当前课程的所有价格策略
        price_policy_dict = {}
        price_policy_queryset = course_obj.price_policy.all()
        for item in price_policy_queryset:
            price_policy_dict[item.id] = {
                'valid_period': item.valid_period,
                'valid_period_text': item.get_valid_period_display(),
                'selected': True if item.id == price_policy_id else False,
                'price': item.price
            }

        # 4. 获取当前购物车的课程信息
        course_info = {
            "id": course_id,
            "name": course_obj.name,
            "course_img": course_obj.course_img,
            "relate_price_policy": price_policy_dict,
            "default_price": price_obj.price,
            "default_price_period": price_obj.valid_period,
            "default_price_policy_id": price_obj.pk
        }

        # 获取缓存中 购物车列表
        shopping_cart_info = CACHE.get(f'SHOPPING_CART_{user_id}')
        if shopping_cart_info:
            shopping_cart_list = json.loads(shopping_cart_info)
        else:
            shopping_cart_list = []
        logger.debug(shopping_cart_list)
        print('-' * 120)
        shopping_cart_list.append(course_info)
        # 5. 存入redis
        # 以SHOPPING_CART_{user_id}为key存储当前用户的购物车数据
        CACHE.set(f'SHOPPING_CART_{user_id}', json.dumps(shopping_cart_list))
        logger.debug(f'set cache for user_id：{user_id}')
        res_obj.msg = '加入购物车成功'
        return Response(res_obj.dict)

    def get(self, request, *args, **kwargs):
        """获取购物车"""
        user_id = request.user.id
        shopping_cart_value = CACHE.get(f'SHOPPING_CART_{user_id}')
        if shopping_cart_value:
            shopping_cart_list = json.loads(shopping_cart_value)
        else:
            shopping_cart_list = []
        print(shopping_cart_list)
        res_obj = BaseResponse()
        res_obj.data = shopping_cart_list
        return Response(res_obj.dict)

    def put(self, request, *args, **kwargs):
        """更新课程的价格策略"""
        res_obj = BaseResponse()
        # 1. 获取课程的id和价格策略的id
        user_id = request.user.id
        course_id = request.data.get('course_id')
        price_policy_id = request.data.get('price_policy_id')
        if not course_id or not price_policy_id:
            res_obj.code = 2003
            res_obj.msg = '无效的参数'
            logger.debug('put shopping cart with no course_id or price_policy_id.')
            return Response(res_obj.dict)
        shopping_cart_value = CACHE.get(f'SHOPPING_CART_{user_id}')
        if shopping_cart_value:
            shopping_cart_list = json.loads(shopping_cart_value)
        else:
            shopping_cart_list = []
        if not shopping_cart_list:
            logger.debug('put shopping cart when shopping_cart_list is Null.')
            res_obj.code = 2004
            res_obj.msg = '无效的参数'
            return Response(res_obj.dict)
        for item in shopping_cart_list:
            if course_id == item['id'] and str(price_policy_id) in item['relate_price_policy']:
                price_policy_obj = models.PricePolicy.objects.filter(id=price_policy_id).first()
                item['default_price_policy_id'] = price_policy_id
                item['default_price_period'] = price_policy_obj.valid_period
                item['default_price'] = price_policy_obj.price
                
                res_obj.msg = '修改购物车成功'
                CACHE.set(f'SHOPPING_CART_{user_id}', json.dumps(shopping_cart_list))
                return Response(res_obj.dict)
        else:
            res_obj.code = 2005
            res_obj.msg = '无效的参数'
            logger.warning('put shopping cart api with invalid course_id or price_policy_id.')
            return Response(res_obj.dict)

    def delete(self, request, *args, **kwargs):
        """删除课程"""
        res_obj = BaseResponse()
        user_id = request.user.id
        course_id = request.data.get('course_id')
        if not course_id:
            res_obj.code = 2003
            res_obj.msg = '无效的参数'
            logger.warning('delete shopping cart with no course_id.')
            return Response(res_obj.dict)

        shopping_cart_value = CACHE.get(f'SHOPPING_CART_{user_id}')
        if shopping_cart_value:
            shopping_cart_list = json.loads(shopping_cart_value)
        else:
            shopping_cart_list = []
        if not shopping_cart_list:
            logger.debug('put shopping cart when shopping_cart_list is Null.')
            res_obj.code = 2004
            res_obj.msg = '无效的参数'
            return Response(res_obj.dict)
        shopping_cart_num = len(shopping_cart_list)
        for i in range(shopping_cart_num):
            if shopping_cart_list[i]['id'] == course_id:
                shopping_cart_list.pop(i)
                res_obj.msg = '更新购物车成功'
                CACHE.set(f'SHOPPING_CART_{user_id}', json.dumps(shopping_cart_list))
                return Response(res_obj.dict)
        else:
            res_obj.code = 2005
            res_obj.msg = '无效的参数'
            logger.warning('delete shopping cart api with invalid course_id.')
            return Response(res_obj.dict)




'''
1 post接口构建数据结构:
    {
        "id": 2,
        "default_price_period": 14,
        "relate_price_policy": {
            "1": {
                "valid_period": 7,
                "valid_period_text": "1周",
                "default": false,
                "prcie": 100.0
            },
            "2": {
                "valid_period": 14,
                "valid_period_text": "2周",
                "default": true,
                "prcie": 200.0
            },
            "3": {
                "valid_period": 30,
                "valid_period_text": "1个月",
                "default": false,
                "prcie": 300.0
            }
        },
        "name": "Django框架学习",
        "course_img": "https://luffycity.com/static/frontend/course/3/Django框架学习_1509095212.759272.png",
        "default_price": 200.0
    }



2 get接口查询数据结构:

[
    {
        "id": "1",
        "name": "Python开发21天入门",
        "course_img": "https://hcdn1.luffycity.com/static/frontend/course/5/21%E5%A4%A9_1544059695.5584881.jpeg",
        "relate_price_policy": {
            "6": {
                "valid_period": 999,
                "valid_period_text": "永久有效",
                "selected": false,
                "price": 0
            },
            "9": {
                "valid_period": 180,
                "valid_period_text": "6个月",
                "selected": false,
                "price": 999
            }
        },
        "default_price": 999,
        "default_price_period": 180,
        "default_price_policy_id": 9
    },
    {
        "id": "2",
        "name": "Linux系统基础5周入门精讲",
        "course_img": "https://hcdn1.luffycity.com/static/frontend/course/12/Linux_1544069008.0915537.jpeg",
        "relate_price_policy": {
            "7": {
                "valid_period": 999,
                "valid_period_text": "永久有效",
                "selected": false,
                "price": 9.99
            }
        },
        "default_price": 9.99,
        "default_price_period": 999,
        "default_price_policy_id": 7
    }
]

'''
