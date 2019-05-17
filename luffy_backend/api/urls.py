#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Q1mi"
# Date: 2019-01-16

from django.conf.urls import url
from api.views import course
from api.views import login
from api.views import shoppingcart
from api.views import checkout
from api.views import trade

urlpatterns = [
    url(r'^course/$', course.CourseListView.as_view()),  # 课程列表
    url(r'^course/category/$', course.CourseCategoryView.as_view()),  # 课程分类列表
    url(r'^course/detail/(?P<pk>\d+)/$', course.CourseDetailView.as_view()),  # 课程详情

    # 极验科技
    url(r'^geetest_check/$', login.pcgetcaptcha),
    url(r'^login/$', login.LoginView.as_view()),

    # 购物车
    url(r'^shoppingcart/$', shoppingcart.ShoppingCartView.as_view()),

    # 结算
    url(r'^checkout/$', checkout.CheckOutView.as_view()),

    # alipay回调
    # url(r'^trade/alipay/$', trade.AliPayTradeView.as_view()),
]
