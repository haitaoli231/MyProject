from django import template
import re
from collections import OrderedDict

register = template.Library()

from django.conf import settings


# 左侧菜单栏
@register.inclusion_tag('rbac/menu.html')
def menu(request):
    # 1. 从session中获取权限信息
    menu_dict = request.session.get(settings.MENU_SESSION_KEY)

    order_dic = OrderedDict()

    # 2. 把权限信息通过 权重 进行排序
    for key in sorted(menu_dict, key=lambda i: menu_dict[i]['weight'], reverse=True):

        order_dic[key] = item = menu_dict[key]

        item['class'] = 'hide'  # 样式: 是否隐藏

        for i in item['children']:
            if i['id'] == request.current_menu_id:
                i['class'] = 'active'  # 样式: 是否凸起
                item['class'] = ''
                break

    return {'menu_list': order_dic.values()}


# 面包屑导航
@register.inclusion_tag('rbac/breadcrumb.html')
def breadcrumb(request):
    # 这里的request.breadcrumb_list是在rbac的中间件中设置的
    return {'breadcrumb_list': request.breadcrumb_list}


# 权限控制到按钮级别
@register.filter
def has_permission(request, name):
    # 如果该按钮对应的url权限在session中的权限信息里面,就返回True,表示允许你显示出来
    # 否则,就不允许显示出来
    if name in request.session[settings.PERMISSION_SESSION_KEY]:
        return True


@register.simple_tag
def gen_role_url(request, rid):
    params = request.GET.copy()
    params['rid'] = rid
    return params.urlencode()
