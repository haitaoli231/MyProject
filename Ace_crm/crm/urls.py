from django.conf.urls import url, include

from crm.views import customer
from crm.views import consult
from crm.views import enrollment
from crm.views import teacher

urlpatterns = [
    # 公户展示
    url(r'customer_list/', customer.CustomerList.as_view(), name='customer_list'),

    # 私户展示
    url(r'my_customer/', customer.CustomerList.as_view(), name='my_customer'),

    # 增加和编辑客户
    url(r'customer_change/(\d+)/', customer.customer_change, name='customer_change'),

    # 展示跟进记录
    url(r'consult_list/(0)/', consult.ConsultList.as_view(), name='all_consult_list'),
    url(r'consult_list/(?P<customer_id>\d+)/', consult.ConsultList.as_view(), name='consult_list'),

    # 增加跟进记录
    url(r'add_consult/', consult.add_consult, name='add_consult'),

    # 编辑跟进记录
    url(r'edit_consult/(\d+)/', consult.edit_consult, name='edit_consult'),

    # 展示报名记录
    url(r'enrollment_list/', enrollment.EnrollmentList.as_view(), name='enrollment_list'),

    # 增加报名记录
    url(r'add_enrollment/(?P<customer_id>\d+)', enrollment.enrollment_change, name='add_enrollment'),

    # 编辑报名记录
    url(r'edit_enrollment/(?P<enrollment_id>\d+)/', enrollment.enrollment_change, name='edit_enrollment'),

    # 展示班级
    url(r'class_list/', teacher.ClassList.as_view(), name='class_list'),

    # 增加班级
    url(r'add_class/', teacher.class_change, name='add_class'),

    # 编辑班级
    url(r'edit_class/(\d+)/', teacher.class_change, name='edit_class'),

    # 展示课程记录
    url(r'course_record_list/(?P<class_id>\d+)/', teacher.CourseRecordList.as_view(), name='course_record_list'),

    # 增加课程记录
    url(r'add_course_record/(?P<class_id>\d+)', teacher.course_record_change, name='add_course_record'),

    # 编辑课程记录
    url(r'edit_course_record/(?P<record_id>\d+)', teacher.course_record_change, name='edit_course_record'),

    # 展示学习记录
    url(r'study_record_list/(?P<course_record_id>\d+)/', teacher.study_record_list, name='study_record_list'),

]
