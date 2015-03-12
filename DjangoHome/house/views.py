#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from django.shortcuts import render
from decimal import Decimal
from house.models import *
from house.forms import *
from django.db.models import Sum

logger = logging.getLogger(__name__)

def project_index(request):
    logger.info("request index")
    form = ProjectSearchForm()
    project_list = Project.objects.all()
    context = {'form': form, 'project_list': project_list}
    return render(request, 'project_index.html', context)

def project_search(request):
    project_list = Project.objects.none()
    is_show_result = False

    if not request.method == 'POST': 
        if 'search-project-post' in request.session: 
            request.POST = request.session['search-project-post'] 
            request.method = 'POST'     # 继续下面 if request.method == 'POST':方法的处理
            is_show_result = True
        else:
            form = ProjectSearchForm(request.POST) # A form bound to the POST data

    if request.method == 'POST':
        form = ProjectSearchForm(request.POST) # A form bound to the POST data
        request.session['search-project-post'] = request.POST
        is_show_result = True
        if form.is_valid(): # All validation rules pass
            keyword = form.cleaned_data['keyword']
            project_list = Project.objects.filter(company__contains=keyword)
            #project_list = set(project_list)  # set用于取唯一,解决上行代码distinct()无法生效问题
            logger.info("search project")

    logger.info("search project 1")

    return render(request, 'project_search.html', {
        'form': form,
        'project_list': project_list,
        'is_show_result': is_show_result
    })

def project_detail(request, project_id):
    project = Project.objects.get(id=project_id)

    project_summary_list = ProjectSummary.objects.all().filter(project_id=project_id)

    dict_building_branch = {}
    building_list = Branch.objects.all().filter(project_id=project_id).values_list('building_name', flat=True).distinct()
            
    context = {'building_list': building_list, 
               'project_summary_list': project_summary_list, 
               'project': project}
    return render(request, 'project_detail.html', context)

def building_detail(request, project_id, building_name):
    project = Project.objects.get(id=project_id)

    # project_summary_list = ProjectSummary.objects.all().filter(project_id=project_id)

    dict_house_list = {}
    for branch in Branch.objects.all().filter(project_id=project_id, building_name=building_name):
        house_list = House.objects.all().filter(branch_id=branch.id)
        dict_house_list[branch.name] = house_list
            
    context = {'dict_house_list': dict_house_list, 
               'building_name': building_name, 
               'project': project}
    logger.error(dict_house_list)
    return render(request, 'building_detail.html', context)

def branch_detail(request, branch_id):
    house_list = House.objects.all().filter(branch_id=branch_id)
    branch_summary_list = BranchSummary.objects.all().filter(branch_id=branch_id)
    context = {'house_list': house_list, 'branch_summary_list': branch_summary_list}
    return render(request, 'branch_detail.html', context)

def company_index(request):
    form = CompanySearchForm()
    company_list = Project.objects.filter().values_list('company', flat=True).distinct()
    #company_list = set(company_list)

    return render(request, 'company_index.html', {
        'form': form,
        'company_list': company_list
    })

def company_detail(request,company_name):
    project_list = Project.objects.filter(company=company_name)
    context = {'project_list': project_list, 'company_name':company_name}
    return render(request, 'company_detail.html', context)


def company_search(request):
    company_list = Project.objects.none()
    is_show_result = False

    if not request.method == 'POST': 
        if 'search-company-post' in request.session: 
            request.POST = request.session['search-company-post'] 
            request.method = 'POST'     # 继续下面 if request.method == 'POST':方法的处理
            is_show_result = True
        else:
            form = CompanySearchForm(request.POST) # A form bound to the POST data

    if request.method == 'POST':
        is_show_result = True
        form = CompanySearchForm(request.POST) # A form bound to the POST data
        request.session['search-company-post'] = request.POST
        if form.is_valid(): # All validation rules pass
            keyword = form.cleaned_data['keyword']
            company_list = Project.objects.filter(company__contains=keyword)\
                .values_list('company', flat=True).distinct()
            #company_list = set(company_list)  # set用于取唯一,解决上行代码distinct()无法生效问题
            logger.info("search company")
    logger.info("search company 1")

    return render(request, 'company_search.html', {
        'form': form,
        'company_list': company_list,
        'is_show_result': is_show_result
    })

def datastat_trend(request):
    return render(request, 'datastat_trend.html')

def datastat_trend_live(request):
    return render(request, 'datastat_trend_live.html')

def datastat_trend_all(request):
    return render(request, 'datastat_trend_all.html')

def datastat_companystat(request):
    company_stat_project = CompanyStat.objects.order_by('-project_count')[:50]
    company_stat_house = CompanyStat.objects.order_by('-house_count')[:50]
    company_stat_size = CompanyStat.objects.order_by('-size_count')[:50]

    return render(request, 'datastat_companystat.html', {
        'company_stat_project': company_stat_project,
        'company_stat_house': company_stat_house,
        'company_stat_size': company_stat_size
    })

def trend_xml_live_count(request):
    trend_data = DataStat.objects.filter(type='住宅').order_by('month')

    return render(request, 'data/live_count.xml', {
        'trend_data': trend_data
    }, content_type="application/xml")
    
def trend_xml_live_size(request):
    trend_data = DataStat.objects.filter(type='住宅').order_by('month')

    return render(request, 'data/live_size.xml', {
        'trend_data': trend_data
    }, content_type="application/xml")
    
def trend_xml_all_count(request):
    trend_data = DataStat.objects.values("month").annotate(TotalHouse=Sum("house_count")).order_by('month')

    return render(request, 'data/all_count.xml', {
        'trend_data': trend_data
    }, content_type="application/xml")
    
def trend_xml_all_size(request):
    trend_data = DataStat.objects.values("month").annotate(TotalSize=Sum("size_count")).order_by('month')

    return render(request, 'data/all_size.xml', {
        'trend_data': trend_data
    }, content_type="application/xml")
    
