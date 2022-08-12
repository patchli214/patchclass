# -*- coding:utf-8 -*-
'''
Created on Aug 16, 2020

@author: patch
'''

from django.db import models
from mongoengine import *

class Teacher(Document):
    login = StringField()
    pw = StringField()
    name = StringField()
    name2 = StringField()
    wechat = StringField()
    tel = StringField()
    email = StringField()
    memo = StringField()
    status = StringField() #-1:离职
    meta = {'collection':'Teacher'}

#付费者、学生联系人（客户）
#===============================================================================
# class Customer(Document):
#     location = StringField()
#     name = StringField()
#     name2 = StringField()
#     wechat = StringField()
#     tel = StringField()
#     email = StringField()
#     meta = {
#         'collection': 'Customer'
#     }
#===============================================================================
#{'location':'','name':'','name2':'','wechat':'','tel':''}}


#学生，一个客户可关联多个学生
class User(Document):
    login = StringField()
    pw = StringField()
    location = StringField() #城市英文，用于获取时区
    timezone = StringField() #时区名
    name = StringField()
    name2 = StringField()
    gender = StringField()
    birthday = DateTimeField()
    wechat = StringField()
    tel = StringField()
    email = StringField()
    status = IntField() #0-未签约 1-签约 2-已学完
    inClass = IntField() #1-在班级中 0-不在班级中
    lessons = IntField() #上过几次课
    customer1 = StringField() #家长1
    customer2 = StringField()
    c1tel = StringField()
    c2tel = StringField()
    c1wechat = StringField()
    c2wichat = StringField()
    c1email = StringField()
    c2email = StringField()
    grade = StringField() #年级 1-12，0：大班，-1：中班
    gradeOneYear = IntField() #入学年份
    isReferrer = IntField() #是否介绍人
    referrer = StringField() #介绍人ID
    referrerName = StringField() #介绍人
    meta = {
        'collection': 'User'
    }

#学生预定课程数
class Contract(Document):
    #customer = ReferenceField(Customer)
    user = ReferenceField(User)
    payTime = DateTimeField()   #缴费日期
    beginDate = DateTimeField()  #开课日期
    lesson = IntField() #共几次课
    validDate = DateTimeField() #有效期截止日
    income = IntField() #实际交费
    payWay = StringField() #付款凭证
    memo = StringField()
    refund = IntField() #转介退款
    refundTime = DateTimeField() #refund日
    meta = {
        'collection': 'Contract'
    }
#转介人礼金
class Bonus(Document):
    userId = StringField()
    userName = StringField()
    contrack = ReferenceField(Contract)
    pay = IntField() #转介费
    payDate = DateTimeField()
    payment = StringField() #付款凭证
    memo = StringField()

#老师的时间与上课学生安排
class Classroom(Document):
    teacher = ReferenceField(Teacher)
    lessonWeekday = IntField()
    lessonTime = StringField()
    users = ListField(ReferenceField(User))
    code = StringField()
    lan = StringField()
    meta = {'collection':'Classroom'}

#课程
class Course(Document):
    name = StringField()
    theme = ListField(StringField())
    skill = ListField(StringField())
    ability = ListField(StringField())
    extention = ListField(StringField())
    content = StringField()
    model = StringField() #模板程序
    attachment = StringField()#图片，声音，视频等资料
    level = IntField()#级别，以1-4数字代表从低到高
    lan = ListField(StringField()) #编程语言
    sensor = ListField(StringField())
    output = ListField(StringField())
    meta = {'collection':'Course'}

#上课整体记录
class Lesson(Document):
    classroom = ReferenceField(Classroom)
    course = ReferenceField(Course)
    teacher = ReferenceField(Teacher)
    lessonDate = DateTimeField()
    memo = StringField()
    meta = {'collection':'Lesson'}

#每个学生的上课记录
class UserLesson(Document):
    user = ReferenceField(User)#出勤同学
    lesson = ReferenceField(Lesson)
    work = StringField()
    memo = StringField()
    theme = ListField(StringField())
    skill = ListField(StringField())
    ability = ListField(StringField())
    lessonDate = DateTimeField()
    media = StringField()
    meta = {'collection':'UserLesson'}
