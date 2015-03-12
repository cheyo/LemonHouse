#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import forms

class ProjectSearchForm(forms.Form):
    keyword = forms.CharField(max_length=100, required=True, 
        widget=forms.TextInput(attrs={'class': 'span4 search-query', 'placeholder': '项目关键字'}))

class CompanySearchForm(forms.Form):
    keyword = forms.CharField(max_length=100, required=True, 
        widget=forms.TextInput(attrs={'class': 'span4 search-query', 'placeholder': '开发商关键字'}))