#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Q1mi"
# Date: 2019-01-23

from rest_framework.views import APIView
from rest_framework.response import Response
from api.auth import LoginAuth
from api.permission import LoginRequire
from api import models
from utils.response import BaseResponse
from utils.exception import LuffyException
import logging
import datetime
import json
from utils.ali.api import ali_api
import time
import random
import django_redis

cache = django_redis.get_redis_connection()


logger = logging.getLogger(__name__)


class PayView(APIView):
    authentication_classes = [LoginAuth, ]
    permission_classes = [LoginRequire, ]

    def _get_pay_url(self, request, order_number, final_price):
        """生成支付宝支付二维码页面URL"""
        if request.META["HTTP_USER_AGENT"]:
            pay_api = ali_api.pay.pc
        elif request == "APP":
            pay_api = ali_api.pay.app
        else:
            pay_api = ali_api.pay.wap
        pay_url = pay_api.direct(
            subject="路飞学城",  # 商品简单描述
            out_trade_no=order_number,  # 商户订单号
            total_amount=final_price,  # 交易金额(单位: 元 保留俩位小数)
        )
        print("pay_url", pay_url)
        return pay_url

    def _get_order_number(self, order_type='1'):
        """生成订单号"""
        now_str = str(round(time.time() * 1000))  # 13位时间戳
        random_str = str(random.randint(1000, 9999))
        return f'{order_type} + {now_str} + {random_str}'

    def _calc_coupon_price(self, o_price, coupon_record_object):
        """
        计算折后价格
        :param o_price: 初始价格
        :param coupon_record_object: 优惠券对象
        :return: 券后价
        """
        coupon_type = coupon_record_object.coupon.coupon_type
        money_equivalent_value = coupon_record_object.coupon.money_equivalent_value
        off_percent = coupon_record_object.coupon.off_percent
        minimum_consume = coupon_record_object.coupon.minimum_consume
        c_price = 0  # 券后价
        if coupon_type == 0:  # 立减券
            c_price = o_price - money_equivalent_value
            if c_price <= 0:
                c_price = 0
        elif coupon_type == 1:  # 满减券
            if minimum_consume > o_price:
                raise LuffyException(4004, "优惠券未达到最低消费")
            else:
                c_price = o_price - money_equivalent_value
        elif coupon_type == 2:  # 折扣券
            c_price = o_price * off_percent / 100
        return c_price

    def post(self, request, *args, **kwargs):
        """
        请求数据格式：
        {
            use_beli:true,
            course_list=[{
                course_id:1
                price_policy_id:1,
                coupon_record_id:2
            },
            {
                course_id:2
                price_policy_id:4,
                coupon_record_id:6
            }],
            common_coupon_id:3,
            pay_money:298
        }
        """
        res_obj = BaseResponse()
        # 1. 获取数据
        course_list = request.data.get('course_list')
        common_coupon_id = request.data.get('common_coupon_id')
        use_beli = request.data.get('use_beli')
        pay_money = request.data.get('pay_money')
        user_id = request.user.id
        # 2. 校验数据
        # 2.2 校验每一个课程
        try:
            course_price_list = []
            for course in course_list:
                course_id = course.get('course_id')
                price_policy_id = course.get('price_policy_id')
                coupon_record_id = course.get('coupon_record_id')
                # 2.2.1 校验课程是否合法
                course_obj = models.Course.objects.filter(id=course_id).first()
                if not course_obj:
                    res_obj.code = 4001
                    res_obj.msg = '支付的课程id无效'
                    logger.warning(f'用户：{user_id} 支付 课程id:{course_id}无效')
                    return Response(res_obj.dict)
                # 2.2.2 校验价格策略是否合法
                course_price_policy = course_obj.price_policy.all()
                price_policy_obj = models.PricePolicy.objects.filter(id=price_policy_id).first()
                if not (price_policy_obj and price_policy_obj in course_price_policy):
                    res_obj.code = 4002
                    res_obj.msg = '支付的价格策略无效'
                    logger.warning(f'用户：{user_id} 支付 无效的价格策略：{price_policy_id}')
                    return Response(res_obj.dict)

                # 2.2.3 校验优惠券是否合法
                # 此处分两种情况
                # 勾选优惠券
                if coupon_record_id:
                    now = datetime.datetime.utcnow()
                    coupon_record_obj = models.CouponRecord.objects.filter(
                        account=request.user,
                        id=coupon_record_id,
                        coupon__content_type__model='course',
                        coupon__object_id=course_id,
                        status=0,
                        coupon__valid_begin_date__lte=now,
                        coupon__valid_end_date__gte=now
                    ).first()
                    if not coupon_record_obj:
                        res_obj.code = 4003
                        res_obj.msg = '课程优惠券无效'
                        logger.warning(f'用户：{user_id}支付 课程：{course_id} 使用课程优惠券：{coupon_record_id} 无效')
                        return Response(res_obj.dict)

                    # 计算折后价格,实现一个方法，传入初始价格和优惠券 返回券后价
                    course_c_price = self._calc_coupon_price(price_policy_obj.price, coupon_record_obj)
                    logger.debug(f'课程：{course_id} 初始价格：{price_policy_obj.price} 使用优惠券：{price_policy_id} 券后价：{course_c_price}')
                    # 课程总价格列表
                    course_price_list.append(course_c_price)
                else:
                    # 没用优惠券,直接加原价
                    course_price_list.append(price_policy_obj.price)

            # 2.2 校验通用优惠券
            # 先求目前课程的所有价格和
            sum_price = sum(course_price_list)
            if common_coupon_id:
                now = datetime.datetime.utcnow()
                common_coupon_obj = models.CouponRecord.objects.filter(
                    account=request.user,
                    id=common_coupon_id,
                    coupon__content_type__model='course',
                    coupon__object_id=None,
                    status=0,
                    coupon__valid_begin_date__lte=now,
                    coupon__valid_end_date__gte=now
                ).first()
                if not common_coupon_obj:
                    logger.warning(f'用户：{user_id}使用了一张无效的通用优惠券：{common_coupon_id}')
                    raise LuffyException(4005, '通用优惠券无效')
                # 利用通用优惠券计算券后总价
                sum_price = self._calc_coupon_price(sum_price, common_coupon_obj)

            # 2.3 校验贝里
            final_price = sum_price
            cost_beli_num = 0  # 花费的贝里数
            if json.loads(use_beli):
                final_price = sum_price - request.user.beli/10
                cost_beli_num = request.user.beli
                if final_price < 0:
                    final_price = 0
                    cost_beli_num = sum_price * 10
            # 2.4 校验最终价格
            if final_price != pay_money:
                raise LuffyException(4006, '支付总价异常')
            # 3. 生成订单
            order_number = self._get_order_number()
            print("order_number", order_number)
            order_obj = models.Order.objects.create(
                payment_type=1,
                order_number=order_number,
                account=request.user,
                status=1,
                order_type=1,
                actual_amount=pay_money,
            )
            print("course_list", course_list)
            # 订单详情
            for course_item in course_list:
                models.OrderDetail.objects.create(
                    order=order_obj,
                    content_type_id=14,
                    object_id=course_item.get("course_id"),
                    original_price=course_item.get("original_price"),
                    price=course_item.get("rebate_price") or course_item.get("original_price"),
                    valid_period=course_item.get("valid_period"),
                    valid_period_display=course_item.get("valid_period_display"),
                )

            request.user.beli = request.user.beli - cost_beli_num
            request.user.save()

            # 将订单号和花费的贝里存入缓存，超时将取消订单 归还贝里和优惠券
            # cache.set(order_number + "|" + str(cost_beli_num), "", 20)
            # 删除之前缓存的结算信息和通用优惠券信息

            cache.delete(f'CHECKOUT_LIST_{user_id}')
            cache.delete(f'COMMON_COUPON_LIST_{user_id}')

            # 4. 返回阿里接口 --> 二维码页面
            res_obj.data = self._get_pay_url(request, order_number, final_price)
        except LuffyException as e:
            res_obj.code = e.code
            res_obj.msg = e.msg
        except Exception as e:
            res_obj.code = 500
            res_obj.msg = str(e)
        return Response(res_obj.dict)







