from django.contrib import admin
from crm import models

admin.site.register(models.UserProfile)     # 用户表
admin.site.register(models.Department)      # 部门表
admin.site.register(models.Campuses)        # 校区表
admin.site.register(models.Customer)        # 客户表
admin.site.register(models.ConsultRecord)   # 跟进记录表
admin.site.register(models.Enrollment)      # 报名表
admin.site.register(models.PaymentRecord)   # 缴费记录表
admin.site.register(models.CourseRecord)    # 课程记录表
admin.site.register(models.StudyRecord)     # 学习记录表
