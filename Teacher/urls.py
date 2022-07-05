'''
Created on Aug 16, 2020

@author: patch
'''
# -*- coding:utf-8 -*-

from django.conf.urls import include, url
from Teacher.views import *

urlpatterns = [

    # reg
    url(r'^editClass$', editClass,name='editClass'),
    url(r'^api_editClass$',api_editClass,name='api_editClass'),
    url(r'^lessonPlan$',lessonPlan,name='lessonPlan'),
    url(r'^lessonCheckin$',lessonCheckin,name='lessonCheckin'),
    url(r'^api_lessonCheckin$',api_lessonCheckin,name='api_lessonCheckin'),
    url(r'^courseList$', courseList,name='courseList'),
    url(r'^courseEdit$', courseEdit,name='courseEdit'),
    url(r'^api_courseEdit$',api_courseEdit,name='api_courseEdit'),
    url(r'^userCoursePlan$', userCoursePlan,name='userCoursePlan'),
    url(r'^userLessonSkill$', userLessonSkill,name='userLessonSkill'),
    url(r'^api_deleteLesson$',api_deleteLesson,name='api_deleteLesson'),
    url(r'^horse$', horse,name='horse'),
    url(r'^swipe$', swipe,name='swipe'),

    ]
app_name = 'Teacher'
