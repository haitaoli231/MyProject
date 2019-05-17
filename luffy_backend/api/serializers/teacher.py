#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Q1mi"
# Date: 2019-01-19

from rest_framework.serializers import ModelSerializer
from api.models import Teacher


class TeacherModelSerializer(ModelSerializer):

    class Meta:
        model = Teacher
        fields = '__all__'
