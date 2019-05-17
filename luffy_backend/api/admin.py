from django.contrib import admin
from api import models
# Register your models here.

admin.site.register(models.UserInfo)
admin.site.register(models.Course)
admin.site.register(models.CourseDetail)
admin.site.register(models.CourseChapter)
admin.site.register(models.CourseSection)
admin.site.register(models.PricePolicy)
admin.site.register(models.Teacher)
admin.site.register(models.CourseCategory)
admin.site.register(models.CouponRecord)
admin.site.register(models.Coupon)
