from django.conf.urls import url
from rbac import views

urlpatterns = [
    # 角色管理
    url(r'role/list/$', views.role_list, name='role_list'),
    # 添加角色
    url(r'role/add/$', views.role_change, name='role_add'),
    # 编辑角色
    url(r'role/edit/(\d+)/$', views.role_change, name='role_edit'),
    # 删除角色
    url(r'role/del/(\d+)/$', views.role_del, name='role_del'),

    # 权限管理
    url(r'menu/list/$', views.menu_list, name='menu_list'),
    # 添加菜单
    url(r'menu/add/$', views.menu_change, name='menu_add'),
    # 编辑菜单
    url(r'menu/edit/(\d+)/$', views.menu_change, name='menu_edit'),
    # 删除菜单
    url(r'^(menu)/del/(\d+)/$', views.delete, name='menu_del'),

    # 添加权限
    url(r'permission/add/$', views.permission_change, name='permission_add'),
    # 编辑权限
    url(r'permission/edit/(\d+)/$', views.permission_change, name='permission_edit'),
    # 删除权限
    url(r'(permission)/del/(\d+)/$', views.delete, name='permission_del'),

    # 批量操作权限
    url(r'multi/permissions/$', views.multi_permissions, name='multi_permissions'),

    # 分配权限
    url(r'distribute/permissions/$', views.distribute_permissions, name='distribute_permissions'),
]
