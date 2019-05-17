from django.shortcuts import render, redirect, HttpResponse, reverse
from crm import models
from crm.forms import ClassForm, CourseRecordForm, StudyRecordForm
from django.http.request import QueryDict
from crm.utils.pagination import Pagination

from crm.utils.urls import reverse_url

from django.views import View
from django.db.models import Q


# 展示班级
class ClassList(View):

    def get(self, request):
        q = self.search([])

        all_class = models.ClassList.objects.filter(q)

        page = Pagination(request.GET.get('page'), all_class.count(), request.GET.copy(), 10)
        return render(request, 'teacher/class_list.html',
                      {'all_class': all_class[page.start:page.end], 'page_html': page.page_html}, )

    def post(self, request):

        action = request.POST.get('action')

        if not hasattr(self, action):
            return HttpResponse('非法操作')

        ret = getattr(self, action)()
        if ret:
            return ret

        return self.get(request)

    def search(self, filed_list):
        query = self.request.GET.get('query', '')
        q = Q()
        q.connector = 'OR'
        for field in filed_list:
            # q.children.append(Q(qq__contains=query))
            q.children.append(Q(('{}__contains'.format(field), query)))
        return q


# 新增/编辑班级
def class_change(request, edit_id=None):
    obj = models.ClassList.objects.filter(pk=edit_id).first()

    form_obj = ClassForm(instance=obj)
    title = '编辑班级' if edit_id else '新增班级'
    if request.method == 'POST':
        form_obj = ClassForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse_url(request, 'class_list'))
    return render(request, 'form.html', {'form_obj': form_obj, 'title': title})


# 展示课程记录
class CourseRecordList(View):

    def get(self, request, class_id):
        q = self.search([])

        all_course_record = models.CourseRecord.objects.filter(q, re_class_id=class_id).order_by('-date')

        page = Pagination(request.GET.get('page'), all_course_record.count(), request.GET.copy(), 10)
        return render(request, 'teacher/course_record_list.html',
                      {'class_id': class_id, 'all_course_record': all_course_record[page.start:page.end],
                       'page_html': page.page_html}, )

    def post(self, request, class_id):

        action = request.POST.get('action')

        if not hasattr(self, action):
            return HttpResponse('非法操作')

        ret = getattr(self, action)()
        if ret:
            return ret

        return self.get(request, class_id)

    def search(self, filed_list):
        query = self.request.GET.get('query', '')
        q = Q()
        q.connector = 'OR'
        for field in filed_list:
            # q.children.append(Q(qq__contains=query))
            q.children.append(Q(('{}__contains'.format(field), query)))
        return q

    def multi_init(self):
        """批量处理学习记录"""
        # 1. 拿到批量处理的所有 课程记录的ID
        course_record_ids = self.request.POST.getlist('ids')  # [1,2 ]

        for course_record_id in course_record_ids:

            # 2. 根据课程记录id拿到每一个课程记录对象
            course_record = models.CourseRecord.objects.filter(pk=course_record_id).first()
            # 3. 根据 课程记录对象 查询出所有学生(客户)对象
            all_student = course_record.re_class.customer_set.filter(status='studying')

            for student in all_student:
                models.StudyRecord.objects.get_or_create(course_record_id=course_record_id, student=student)


def course_record_change(request, class_id=None, record_id=None):
    obj = models.CourseRecord.objects.filter(pk=record_id).first() if record_id else models.CourseRecord(
        re_class_id=class_id, teacher=request.user_obj)
    form_obj = CourseRecordForm(instance=obj)
    title = '编辑课程记录' if record_id else '添加课程记录'
    if request.method == 'POST':
        form_obj = CourseRecordForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse_url(request, 'course_record_list', class_id))
    return render(request, 'form.html', {'form_obj': form_obj, 'title': title})


from django.forms import modelformset_factory


def study_record_list(request, course_record_id):
    FormSet = modelformset_factory(models.StudyRecord, StudyRecordForm, extra=0)

    all_study_record = models.StudyRecord.objects.filter(course_record_id=course_record_id)

    form_obj = FormSet(queryset=all_study_record)

    if request.method == 'POST':
        form_obj = FormSet(request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('study_record_list', args=(course_record_id,)))

    return render(request, 'teacher/study_record_list.html', {'form_obj': form_obj}, )
