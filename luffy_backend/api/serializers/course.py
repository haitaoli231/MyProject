#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Q1mi"
# Date: 2019-01-16

from rest_framework import serializers
from api import models
from api.serializers.teacher import TeacherModelSerializer


class CourseModelSerializer(serializers.ModelSerializer):
    level = serializers.CharField(source='get_level_display')
    coursedetail_id = serializers.IntegerField(source='coursedetail.id')
    learn_num = serializers.IntegerField(source='order_details.count')

    class Meta:
        model = models.Course
        fields = '__all__'

    def to_representation(self, instance):
        """自定修改系列化结果"""
        data = super(CourseModelSerializer, self).to_representation(instance)

        # 获取价格套餐
        price_policy = instance.price_policy.order_by("valid_period").only("price", "valid_period").last()
        data["has_price"] = True
        # 如果没有价格套餐
        if not price_policy:
            data["has_price"] = False
            return data
        # 价格
        data["price"] = "{:.2f}".format(price_policy.price)
        # 有效期
        data["valid_period"] = price_policy.valid_period
        return data


class CourseDetailModelSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='course.name')
    price = serializers.SerializerMethodField()
    level = serializers.CharField(source='course.level')
    teachers = serializers.SerializerMethodField()
    recommend_courses = serializers.SerializerMethodField()
    brief = serializers.CharField(source='course.brief')
    course_img = serializers.CharField(source='course.course_img')

    def get_price(self, instance):
        return [{
            'price': item.price,
            'valid_period': item.valid_period,
            'valid_period_text': item.get_valid_period_display(),
        } for item in instance.course.price_policy.all()]

    def get_teachers(self, instance):
        return TeacherModelSerializer(instance.teachers.all(), many=True).data

    def get_recommend_courses(self, instance):
        return [{
            'id': item.id,
            'name': item.name,
        } for item in instance.recommend_courses.all()]

    class Meta:
        model = models.CourseDetail
        fields = '__all__'


class CourseCategoryModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CourseCategory
        fields = '__all__'


