# from django.contrib.auth.middleware import AuthenticationMiddleware

from django.utils.deprecation import MiddlewareMixin
from crm import models
from django.shortcuts import redirect, reverse


class AuthenticationMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # 拿到id 获取到对象

        # 如果该用户访问的当前路径是login或reg或admin就直接通过
        if request.path_info in [reverse('login'), reverse('reg')] or request.path_info.startswith('/admin/'):
            return

        # 从session中获取用户pk
        pk = request.session.get('pk')
        # 去数据库中校验该用户是否存在
        obj = models.UserProfile.objects.filter(pk=pk).first()
        if obj:
            request.user_obj = obj
            return
        # 如果session中用户与数据库不匹配就 重新登录
        return redirect(reverse('login'))
