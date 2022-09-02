#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
Created on Sep 15, 2020

@author: patch
'''
#import datetime
from django import template
from Tool import constant,util
from Tool.models import Teacher, User
from django.template.defaultfilters import stringfilter


register = template.Library()

@register.filter
def week_name(value):
    week = ["", "一", "二", "三", "四", "五", "六", "日"]
    if value:
        day = int(value)
        if day >= 1 and day <= 7:
            return week[day]
        else:
            return ""

    else:
        return ""

@register.filter
@stringfilter
def get_name(key,type):
  try:
    if type=='lan':
        return constant.LAN[key]
    if type=='skill':
        return constant.SKILL[key]
    if type=='ability':
        return constant.ABILITY[key]
    if type=='theme':
        return constant.THEME[key]
    if type=='extention':
        return constant.EXTENTION[key]
    if type=='sensor':
        return constant.SENSOR[key]
    if type=='output':
        return constant.OUTPUT[key]
    if type=='grade':
        return constant.GRADE[key]
  except Exception as e:
      print (e)
      return ''



@register.filter
def get_localtime(utc_dt,timezone):
    t = None
    if timezone and len(timezone) > 1:
        t = util.utc_to_local(utc_dt,timezone)
    else:
        t = util.utc_to_local(utc_dt,None)
    return t.strftime("%Y-%m-%d")
