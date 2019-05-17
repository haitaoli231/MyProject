#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Q1mi"
# Date: 2019-01-20

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import logging
from api.models import Token
import datetime
from django.core.cache import cache
logger = logging.getLogger(__name__)


class LoginAuth(BaseAuthentication):
    def authenticate(self, request):
        """
        1. 对Token做有效性校验
        2. 将Token缓存起来
        :param request:
        :return:
        """
        token = request.META.get('HTTP_AUTHTOKEN')
        logger.debug(token)
        user_obj = cache.get(token)
        if user_obj:
            logger.debug('token in cache')
            return user_obj, token
        token_obj = Token.objects.filter(key=token).first()
        if not token_obj:
            raise AuthenticationFailed('认证失败')
        # 判断token是否在有效期中
        logger.debug(token_obj.created)
        now = datetime.datetime.now(datetime.timezone.utc)
        passed = now - token_obj.created  # token创建到现在过去了多久
        logger.debug(f'token has been created:{passed}')
        is_valid = passed < datetime.timedelta(weeks=2)
        logger.debug(f'token valid:{is_valid}')
        if is_valid:
            # 设置cache缓存
            delta = datetime.timedelta(weeks=2) - passed
            cache.set(token_obj.key, token_obj.user, min(delta.total_seconds(), 60*24*14))
            return token_obj.user, token_obj.key
        else:
            raise AuthenticationFailed('Token过期')
