# -*- coding:utf-8 -*-
'''
Created on Aug 16, 2020

@author: patch
'''
from time import mktime
from geopy.geocoders import GeoNames
import json,datetime,time
from tzlocal import get_localzone
#from models import Teacher
from django.http import HttpResponse
import hashlib
import pytz 
from Tool.models import Course

def changeThemeToList():
    courses = Course.objects.all()  # @UndefinedVariable
    for c in courses:
        #if isinstance(c.skill,unicode):
            c.delete()
            continue
        #if isinstance(c.theme,unicode):
            c.theme = [c.theme]
            c.save()

if __name__ == "__main__":
    changeThemeToList()