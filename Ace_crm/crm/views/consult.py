from django.shortcuts import render, redirect, HttpResponse, reverse
from crm import models
from crm.forms import ConsultForm
from django.http.request import QueryDict
from crm.utils.pagination import Pagination

from crm.utils.urls import reverse_url

from django.views import View
from django.db.models import Q


# 展示跟进记录
class ConsultList(View):

    def get(self, request, customer_id):

        q = self.search([])  # 模糊查询

        if customer_id == '0':
            all_consult = models.ConsultRecord.objects.filter(q, delete_status=False,
                                                              consultant=request.user_obj).order_by('-date')
        else:
            all_consult = models.ConsultRecord.objects.filter(q, delete_status=False, customer_id=customer_id,
                                                              consultant=request.user_obj).order_by('-date')

        page = Pagination(request.GET.get('page'), all_consult.count(), request.GET.copy(), 10)
        return render(request, 'consultant/consult_list.html',
                      {'all_consult': all_consult[page.start:page.end], 'page_html': page.page_html}, )

    def post(self, request, customer_id):

        action = request.POST.get('action')

        if not hasattr(self, action):
            return HttpResponse('非法操作')

        getattr(self, action)()

        return self.get(request, customer_id)

    def search(self, filed_list):
        query = self.request.GET.get('query', '')
        q = Q()
        q.connector = 'OR'
        for field in filed_list:
            # q.children.append(Q(qq__contains=query))
            q.children.append(Q(('{}__contains'.format(field), query)))
        return q


# 增加跟进记录
def add_consult(request):
    obj = models.ConsultRecord(consultant=request.user_obj)

    form_obj = ConsultForm(instance=obj)
    if request.method == 'POST':
        form_obj = ConsultForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()

            return redirect(reverse_url(request, 'consult_list'))

    return render(request, 'consultant/add_consult.html', {'form_obj': form_obj})

# 编辑跟进记录
def edit_consult(request, edit_id):
    obj = models.ConsultRecord.objects.filter(pk=edit_id).first()

    form_obj = ConsultForm(instance=obj)
    if request.method == 'POST':
        form_obj = ConsultForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()

            return redirect(reverse_url(request, 'consult_list'))

    return render(request, 'consultant/edit_consult.html', {'form_obj': form_obj})
