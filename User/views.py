# -*- coding:utf-8 -*-
'''
Created on Aug 16, 2020

@author: patch
'''
import json,time,datetime
from Tool import constant,models,util
from django import forms
from django.views.decorators.csrf import  csrf_exempt
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render
from Tool.models import Teacher, Classroom, User,Lesson, Course, UserLesson
from mongoengine.queryset.visitor import Q
from django.utils.dateparse import parse_datetime

def index(request):
    return render(request, 'index.html', {})


def userList(request):
    login_teacher = util.checkCookie(request)
    if not (login_teacher):
        return HttpResponseRedirect('/login')
    inClass = request.GET.get("inClass")
    paid = request.GET.get("paid")
    learned = request.GET.get("learned")

    status = request.GET.get("status")
    query = Q(status__gt=-1)
    title = u'全部'

    other = {'?inClass=1':u'在班学生','?learned=1':u'学过','?paid=1':u'付费'}

    if inClass == '1':
        title = u'在班学生'
        other = {'?':u'全部','?learned=1':u'学过','?paid=1':u'付费'}
        query = query&Q(inClass=1)
    if learned == '1':
        title = u'学过'
        other = {'?':u'全部','?inClass=1':u'在班学生','?paid=1':u'付费'}
        query = query&Q(lessons__gt=0)

    if paid == '1':
        title = u'付费'
        other = {'?':u'全部','?inClass=1':u'在班学生','?learned=1':u'学过'}
        query = query&Q(status=1)

    if inClass == '0':
        query = query&Q(inClass__ne=1)


    users = User.objects.filter(query)  # @UndefinedVariable

    temp = []
    for u in users:
        grade = getGrade(u.gradeOneYear)
        if grade:
            u.grade = str(grade)
        dateNow = util.getDateNow()
        try:
            days = (dateNow-u.birthday).days
            u.year = str(days/365)
        except:
            err = 1
        u.referrerName = ''
        if u.referrer:
            try:
                rr = User.objects.get(id=u.referrer)
                u.referrerName = rr.name
            except Exception, e:
                print(e)
                u.referrerName = ''
        if u.referrer:
            print('[u.referrer-----------]')
            print(u.referrerName)
        temp.append(u)
    users = temp
    return render(request, 'userList.html', {"login_teacher":login_teacher,"users":users,
                                             "title":title,"other":other})

def userEdit(request):
    login_teacher = util.checkCookie(request)
    if not (login_teacher):
        return HttpResponseRedirect('/login')
    userId = request.GET.get("userId")
    user = None
    try:
        user = User.objects.get(id=userId)  # @UndefinedVariable
        grade = getGrade(user.gradeOneYear)
        if grade:
            user.grade = str(grade)

    except:
        user = None
    refs = None
    try:
        query = Q(isReferrer=1)&Q(id__ne=userId)
        refs = User.objects.filter(query)
    except:
        refs = None
    #return render(request, 'userEdit.html')
    return render(request, 'userEdit.html', {"login_teacher":login_teacher,"grades":constant.GRADE,"refs":refs,"user":user})

@csrf_exempt
def api_userEdit(request):
    login_teacher = util.checkCookie(request)
    if not (login_teacher):
        return HttpResponseRedirect('/login')


    userId = request.POST.get("userId")
    name = request.POST.get("name")
    name2 = request.POST.get("name2")
    gender = request.POST.get("gender")
    grade = request.POST.get("grade")
    if not grade or grade == '':
        grade = ''

    birthdayStr = request.POST.get("birthday")
    birthday = None
    try:
        birthday = util.local_to_utc(birthdayStr + " 12:00:00","Asia/Shanghai")
    except:
        birthday = None
    location = request.POST.get("location")
    timezone = request.POST.get("timezone")
    customer1 = request.POST.get("customer1")
    c1tel = request.POST.get("c1tel")
    c1email =  request.POST.get("c1email")
    c1wechat = request.POST.get("c1wechat")
    statusStr  =  request.POST.get("status")
    gradeOneYear = getGradeOneYear(grade)
    referrer = None
    print('[--------status-----------------]')
    print(statusStr)
    try:
        status = int(statusStr)
        print(status)

    except Exception as e:
        print(e)
        status = 0

    isReferrerStr = request.POST.get("isReferrer")
    try:
        if isReferrerStr == "true":
            isReferrer = 1
        else:
            isReferrer = 0

    except Exception as e:
        print(e)
        isReferrer = 0

    user = None
    try:
        user = User.objects.get(id=userId)  # @UndefinedVariable
    except:
        user = User()

    referrer = request.POST.get("referrer")
    try:
        ref = User.objects.get(id=referrer)  # @UndefinedVariable
    except:
        ref = None

    if gradeOneYear:
        user.gradeOneYear = gradeOneYear

    user.name = name
    user.name2 = name2
    user.location = location
    user.timezone = timezone
    user.gender = gender
    user.birthday = birthday
    user.customer1 = customer1
    user.c1tel = c1tel
    user.c1email = c1email
    user.c1wechat = c1wechat
    user.status = status
    user.isReferrer = isReferrer
    if ref:
        user.referrer = str(ref.id)
    else:
        user.referrer = None

    user.save()

    res = {"error": 0, "msg": "OK"}
    return util.JSONResponse(json.dumps(res, ensure_ascii=False))

def profile(request):
    login_teacher = util.checkCookie(request)
    userId = request.GET.get("userId")
    userName = request.GET.get("name")

    user = None
    try:
        user = User.objects.get(id=userId)  # @UndefinedVariable
    except:
        try:

            if userName and userName !='':
                query = Q(name__icontains=userName)|Q(name2__icontains=userName)
                user = User.objects.filter(query)[0]  # @UndefinedVariable

            else:
                user = None

                return render(request, 'profile.html',{"user":user})
        except:
            user = None
            return render(request, 'profile.html',{"user":user})

    query = Q(user=user.id)
    lessons = UserLesson.objects.filter(query).order_by("-lessonDate")  # @UndefinedVariable
    #lessons = UserLesson.objects.all().order_by("-lessonDate")  # @UndefinedVariable
    ttt = []
    for l in lessons:
        l = getMediaType(l)
        if not l.lessonDate:
            l.lessonDate = l.lesson.lessonDate
            l.save()
        if l.lessonDate:
            l.lessonDate = util.utc_to_local(l.lessonDate, None)
            ttt.append(l)
    query = Q(users__contains=userId)
    classrooms = Classroom.objects.filter(query)  # @UndefinedVariable
    now = datetime.datetime.now()
    dateStr = datetime.datetime.strftime(now,"%Y-%m-%d")
    temp = []
    for c in classrooms:
        #dateBeijing = datetime.datetime.strptime(dateStr + " " + c.lessonTime + ":00","%Y-%m-%d %H:%M:%S")
        date = util.local_to_utc(dateStr + " " + c.lessonTime + ":00","Asia/Shanghai")
        dateLocal = util.utc_to_local(date, user.timezone)
        dateBeijing = util.utc_to_local(date, "Asia/Shanghai")
        delta = c.lessonWeekday-(dateBeijing.weekday()+1)

        dateLocal = dateLocal + datetime.timedelta(days=delta)
        dateBeijing = dateBeijing + datetime.timedelta(days=delta)


        c.lessonWeekday = dateLocal.weekday()+1
        c.lessonTime = datetime.datetime.strftime(dateLocal,"%H:%M")
        temp.append(c)


    return render(request, 'profile.html', {"lessons":ttt,"login_teacher":login_teacher,
                                                  "classrooms":temp,"user":user})

def work(request):
    userId = request.GET.get("userId")
    lessonId = request.GET.get("lessonId")
    userLesson = None
    query = Q(user=userId)&Q(lesson=lessonId)
    try:
        userLesson = UserLesson.objects.get(query)  # @UndefinedVariable
        userLesson = getMediaType(userLesson)

        #=======================================================================
        # userLesson.mediaType = ''
        # if userLesson.media:
        #   if userLesson.media.find(".mp4") > -1:
        #     userLesson.mediaType = 'video'
        #   elif userLesson.media.find(".png") > -1 or userLesson.media.find(".jpg") > -1 or userLesson.media.find(".gif") > -1 or userLesson.media.find(".svg") > -1 or userLesson.media.find(".jpeg") > -1:
        #     userLesson.mediaType = 'image'
        #=======================================================================

    except Exception as e:
        print(e)
        userLesson = None
        return render(request, 'work.html')

    return render(request, 'work.html', {"lesson":userLesson.lesson,"course":userLesson.lesson.course,
                                                  "userLesson":userLesson,"user":userLesson.user})
def getMediaType(userLesson):
    userLesson.mediaType = ''
    if userLesson.media:
          if userLesson.media.find(".mp4") > -1:
            userLesson.mediaType = 'video'
          elif userLesson.media.find(".png") > -1 or userLesson.media.find(".jpg") > -1 or userLesson.media.find(".gif") > -1 or userLesson.media.find(".svg") > -1 or userLesson.media.find(".jpeg") > -1:
            userLesson.mediaType = 'image'
    return userLesson

def userSkill(request):
    userId = request.GET.get("userId")
    query = Q(user=userId)
    userLessons = UserLesson.objects.filter(query)  # @UndefinedVariable
    query = Q(id=userId)
    user = None
    skill = {}
    theme = {}
    ability = {}
    try:
        user = User.objects.get(query)  # @UndefinedVariable
        j = 0
        for c in userLessons:
            j = j + 1
            temp = []
            for s in c.skill:
                try:
                    skill[s] = skill[s] + 1
                except:
                    skill[s] = 1
        for i, (key, value) in enumerate(constant.SKILL.iteritems()):
            try:
                print(skill[key])
            except:
                skill[key] = 0
    except:
        err = 1

    return render(request, 'userSkill.html', {"skill":skill,"user":user})

def getGradeOneYear(gradeNow):
    try:
        grade = int(gradeNow)
        now = util.getDateNow()
        afterSep = datetime.datetime.strptime(str(now.year)+'0901000000','%Y%m%d%H%M%S')
        if now < afterSep:
            return now.year - grade
        else:
            return now.year - grade + 1
    except Exception as e:
        print(e)
        return None

def getGrade(gradeOneYear):
    try:
            now = util.getDateNow()
            grade = now.year - gradeOneYear
            if now >= datetime.datetime.strptime(str(now.year)+'0901000000','%Y%m%d%H%M%S'):
                grade = grade + 1
            grade = str(grade)
    except:
            grade = None
    return grade
