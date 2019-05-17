# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2019-01-19 07:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='coursecategory',
            options={'verbose_name': '课程分类', 'verbose_name_plural': '课程分类'},
        ),
        migrations.AlterField(
            model_name='pricepolicy',
            name='valid_period',
            field=models.SmallIntegerField(choices=[(1, '1天'), (3, '3天'), (7, '1周'), (14, '2周'), (30, '1个月'), (60, '2个月'), (90, '3个月'), (120, '4个月'), (180, '6个月'), (210, '12个月'), (540, '18个月'), (720, '24个月'), (722, '24个月'), (723, '24个月'), (999, '永久有效')], default=999),
        ),
    ]
