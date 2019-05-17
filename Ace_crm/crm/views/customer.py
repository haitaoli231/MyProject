from django.shortcuts import render, redirect, HttpResponse, reverse
from crm import models
from crm.forms import CustomerForm
from django.http.request import QueryDict
from crm.utils.pagination import Pagination
from crm.utils.urls import reverse_url
from django.db import transaction
from django.views import View
from django.db.models import Q
from django.conf import settings, global_settings


# 客户展示
class CustomerList(View):

    def get(self, request):
        q = self.search(['qq', 'name', ])

        # 1. 如果是公户
        if request.path_info == reverse('customer_list'):
            # 1.1 查询出所有 没有销售在跟进的 客户
            all_customer = models.Customer.objects.filter(q, consultant__isnull=True, )
        # 2. 如果是私户
        else:
            # 2.1 查询出所有 当前用户正在跟进的 客户
            all_customer = models.Customer.objects.filter(q, consultant=request.user_obj)

        # 3. 将需要展示的数据交给分页器 进行分页展示
        page = Pagination(request.GET.get('page'), all_customer.count(), request.GET.copy(), 10)
        # 4. 跳转到 客户展示页面
        return render(request, 'consultant/customer_list.html',
                      {'all_customer': all_customer[page.start:page.end], 'page_html': page.page_html}, )

    def post(self, request):
        # 1. 获取前端提交的行为: action的值要么是multi_apply要么是multi_pub
        action = request.POST.get('action')

        # 2. 如果当前用户没有action对应的权限,返回错误信息
        if not hasattr(self, action):
            return HttpResponse('非法操作')

        # 3. 如果当前用户有action对应的权限,执行该行为
        ret = getattr(self, action)()
        if ret:
            return ret

        return self.get(request)

    def multi_apply(self):
        """公户变私户"""
        # 1. 获取批量操作拿到的所有 客户id
        ids = self.request.POST.getlist('ids')  # ids是列表

        # 2. 当前销售私户的数量 + 申请的客户的数量 > 上限
        if self.request.user_obj.customers.all().count() + len(ids) > settings.MAX_CUSTOMER_NUM:
            return HttpResponse('做人不要太贪心了，给别人留点')

        # 3. 开启事务
        with transaction.atomic():
            # 3.1 根据ids去数据库中查找客户对象,返回一个queryset
            queryset = models.Customer.objects.filter(pk__in=ids, consultant__isnull=True).select_for_update()  # 加行锁
            # 3.2 判断提交的 ids的长度 和 查询出的数据数量 是否一致
            if len(ids) == queryset.count():
                # 3.3 如果一致,就把queryset中的所有客户对象的 销售 变更为 当前用户
                queryset.update(consultant=self.request.user_obj)
                return
            return HttpResponse('你的手速太慢,已经别别人掳走了')

    def multi_pub(self):
        """私户变公户: 把客户对象的销售人员删除,该客户就变成公户了"""
        ids = self.request.POST.getlist('ids')
        # 方式一
        # models.Customer.objects.filter(pk__in=ids).update(consultant=None)

        # 方式二
        self.request.user_obj.customers.remove(*models.Customer.objects.filter(pk__in=ids))

    def search(self, field_list):
        """
        搜索功能
        参数field_list表示在哪些个字段范围内进行搜索
        """
        # 1. 获取前端提交的要搜索的字段
        query = self.request.GET.get('query', '')
        # 2. 实例化Q对象
        q = Q()
        q.connector = 'OR'
        # 3. 设置搜索范围: 例如field_list=['qq', 'name', ] 表示只能在客户的qq和name里面进行搜索
        for field in field_list:
            q.children.append(Q(('{}__contains'.format(field), query)))
        return q


# 增加客户
def add_customer(request):
    # 实例化CustomerForm
    form_obj = CustomerForm()

    if request.method == 'POST':
        # 1. 将前端提交的数据交给CustomerForm对象 并实例化
        form_obj = CustomerForm(request.POST)
        # 2. 对数据进行校验
        if form_obj.is_valid():
            # 2.1 校验成功执行新增
            form_obj.save()
            # 2.2 新增成功跳转到客户展示页面
            return redirect(reverse_url(request, 'customer_list'))

    return render(request, 'consultant/add_customer.html', {'form_obj': form_obj})


# 编辑客户
def edit_customer(request, edit_id):
    # 1. 从数据库中查询出要修改的客户对象
    obj = models.Customer.objects.filter(pk=edit_id).first()
    # 2. 将客户交给Form对象并实例化(为了在编辑页面展示原始数据)
    form_obj = CustomerForm(instance=obj)

    if request.method == 'POST':
        # 3. 提交修改后数据的和原始的数据
        form_obj = CustomerForm(request.POST, instance=obj)
        # 4. 校验提交的数据
        if form_obj.is_valid():
            # 4.1 校验成功保存
            form_obj.save()
            # 4.2 跳转到客户展示页面
            return redirect(reverse_url(request, 'customer_list'))

    return render(request, 'consultant/edit_customer.html', {'form_obj': form_obj})


# 新增和编辑客户
def customer_change(request, edit_id=None):
    # 1. 去数据库查询edit_id对应的客户对象是否存在
    obj = models.Customer.objects.filter(pk=edit_id).first()

    # 2. 不管存在与否都将查询出来的结果交给Form对象
    form_obj = CustomerForm(instance=obj)

    # 3. 如果edit_id存在表示编辑客户,反之表示新增客户
    title = '编辑客户' if edit_id else '新增客户'

    if request.method == 'POST':
        # 4. 将提交的数据和原始数据交给Form对象实例化
        form_obj = CustomerForm(request.POST, instance=obj)
        # 5. 校验数据
        if form_obj.is_valid():
            # 5.1 校验成功保存数据
            form_obj.save()
            # 5.2 跳转到客户展示页面
            return redirect(reverse('customer_list'))

    return render(request, 'consultant/customer_change.html', {'form_obj': form_obj, 'title': title})
