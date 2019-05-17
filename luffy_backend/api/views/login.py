#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Q1mi"
# Date: 2019-01-17

"""
登录认证接口
"""
from django.contrib import auth
from utils.geetest import GeetestLib
from django import views
from django.shortcuts import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
import uuid
from api.models import Token
from utils.response import BaseResponse

pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"


def pcgetcaptcha(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    # 设置 geetest session, 用于是否启用滑动验证码向 geetest 发起远程验证, 如果取不到的话只是对本地轨迹进行校验
    # request.session[gt.GT_STATUS_SESSION_KEY] = status
    # request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)


class LoginView(APIView):
    @property
    def generate_key(self):
        return uuid.uuid1().hex

    def post(self, request):
        res_obj = BaseResponse()
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.data.get(gt.FN_CHALLENGE, '')
        validate = request.data.get(gt.FN_VALIDATE, '')
        seccode = request.data.get(gt.FN_SECCODE, '')
        # status = request.session[gt.GT_STATUS_SESSION_KEY]
        # user_id = request.session["user_id"]
        # result = gt.failback_validate(challenge, validate, seccode)
        result = gt.success_validate(challenge, validate, seccode, None)
        print(result)
        if result:
            username = request.data.get('username')
            pwd = request.data.get('password')
            print(username, pwd)
            user_obj = auth.authenticate(username=username, password=pwd)
            if user_obj:
                # 创建Token
                token = self.generate_key
                import datetime
                now = datetime.datetime.now()
                Token.objects.update_or_create(user=user_obj, defaults={"key": token, "created": now})
                res_obj.data = token
            else:
                res_obj.code = 1002
                res_obj.msg = '用户名或密码错误'
        else:
            res_obj.code = 1003
            res_obj.msg = '请滑动验证码'

        return Response(res_obj.dict)