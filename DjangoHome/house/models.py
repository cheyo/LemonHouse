#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models

# Create your models here.
class Project(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100,db_index=True)
    region = models.CharField(max_length=10)
    approved_date = models.DateField()

    class Meta:
        ordering = ["-approved_date"]

class ProjectSummary(models.Model):
    type = models.CharField(max_length=50)
    min_size = models.DecimalField(max_digits = 10, decimal_places = 2)
    max_size = models.DecimalField(max_digits = 10, decimal_places = 2)
    min_price = models.DecimalField(max_digits = 10, decimal_places = 2, null=True)
    max_price = models.DecimalField(max_digits = 10, decimal_places = 2, null=True)
    avg_price = models.DecimalField(max_digits = 10, decimal_places = 2, null=True)
    sample_count = models.IntegerField()
    total_count = models.IntegerField()
    project = models.ForeignKey(Project,db_index=True)

class Branch(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    md5 = models.CharField(max_length=32)
    building_name = models.CharField(max_length=100)
    project = models.ForeignKey(Project,db_index=True)

class BranchSummary(models.Model):
    type = models.CharField(max_length=50)
    min_size = models.DecimalField(max_digits = 10, decimal_places = 2)
    max_size = models.DecimalField(max_digits = 10, decimal_places = 2)
    min_price = models.DecimalField(max_digits = 10, decimal_places = 2, null=True)
    max_price = models.DecimalField(max_digits = 10, decimal_places = 2, null=True)
    avg_price = models.DecimalField(max_digits = 10, decimal_places = 2, null=True)
    sample_count = models.IntegerField()
    total_count = models.IntegerField()
    branch = models.ForeignKey(Branch,db_index=True)

class House(models.Model):
    sn = models.AutoField(primary_key=True)
    id = models.IntegerField(null=False,unique=True)
    name = models.CharField(max_length=50)
    floor = models.CharField(max_length=50)
    size1 = models.DecimalField(max_digits = 10, decimal_places = 2)
    size2 = models.DecimalField(max_digits = 10, decimal_places = 2)
    size3 = models.DecimalField(max_digits = 10, decimal_places = 2)
    price = models.DecimalField(max_digits = 12, decimal_places = 2, null=True)
    type = models.CharField(max_length=50)
    STATUS = (
        (1, '期房待售'),
        (2, '已签预售合同'),
        (3, '已签认购书'),
        (4, '已备案'),
        (5, '初始登记'),
        (6, '管理局锁定'),
        (7, '自动锁定'),
        (8, '安居房'),
        (999, '未知'),
    )
    status = models.IntegerField(choices=STATUS)
    branch = models.ForeignKey(Branch,db_index=True)

    class Meta:
        ordering = ["sn"]

class DataStat(models.Model):
    month = models.CharField(max_length=20)
    type = models.CharField(max_length=50)
    house_count = models.IntegerField()
    size_count = models.DecimalField(max_digits = 10, decimal_places = 2, null=True)

class CompanyStat(models.Model):
    company = models.CharField(max_length=100,db_index=True)
    project_count = models.IntegerField()
    house_count = models.IntegerField(null=True)
    size_count = models.DecimalField(max_digits = 10, decimal_places = 2, null=True)

class SystemStatus(models.Model):
    id = models.IntegerField(primary_key=True)
    last_update = models.DateField()
