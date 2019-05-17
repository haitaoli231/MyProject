from django.shortcuts import render, redirect, HttpResponse, reverse
from crm import models
from crm.forms import RegForm
import hashlib
from django.views.decorators.csrf import ensure_csrf_cookie
from rbac.service.permission import init_permission


def index(request):
    return HttpResponse('index')


# @ensure_csrf_cookie
def login(request):
    if request.method == 'POST':
        # 1. 获取前端post请求提交的 用户名和密码
        user = request.POST.get('username')
        pwd = request.POST.get('password')

        md5 = hashlib.md5()
        md5.update(pwd.encode('utf-8'))
        pwd = md5.hexdigest()

        # 2. 去数据库匹配 该用户名和密码 对应的用户对象 是否存在
        obj = models.UserProfile.objects.filter(username=user, password=pwd, is_active=True).first()
        print(obj.name)
        if obj:  # 若用户对象存在
            # 3.1 把该用户的 pk 保存到session中
            request.session['pk'] = obj.pk
            # 3.2 初始化权限信息: 通过用户对象查询到该用户的权限信息,重新构建权限信息字典和菜单信息字典并将之保存到session中
            init_permission(request, obj)
            # 3.3 登录成功, 跳转到客户展示页面
            return redirect(reverse('customer_list'))

    return render(request, 'login.html')


def reg(request):
    # 1. 实例化RegForm
    form_obj = RegForm()

    if request.method == 'POST':
        # 2. 将post请求提交的数据交给RegForm重新实例化
        form_obj = RegForm(request.POST)
        # 3. 如果form组件校验成功
        if form_obj.is_valid():
            """
            # 插入到数据库
            # print(form_obj.cleaned_data)
            # form_obj.cleaned_data.pop('re_pwd')
            # models.UserProfile.objects.create(**form_obj.cleaned_data)
            """
            # 3.1 将校验成功的数据保存到数据库中
            form_obj.save()
            # 3.2 跳转到登录页面进行登录
            return redirect(reverse('login'))

    return render(request, 'reg.html', {'form_obj': form_obj})


# 注销
def logout(request):
    request.session.flush()
    return redirect(reverse('login'))
