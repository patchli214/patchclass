# -*- coding:utf-8 -*-
'''
Created on Aug 16, 2020

@author: patch
'''
from time import mktime
from geopy.geocoders import GeoNames
import json,datetime,time
from tzlocal import get_localzone
from Tool.models import Teacher,User
from django.http import HttpResponse
import hashlib
import pytz
from Tool.models import Classroom,User
import random


class JSONResponse(HttpResponse):
    def __init__(self, obj):
        if isinstance(obj, dict):
            _json_str = json.dumps(obj)
        else:
            _json_str = obj
        super(JSONResponse, self).__init__(_json_str, content_type="application/json;charset=utf-8")

def str2md5(str):
    try:
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()
    except:
        return None


def checkCookie(request):
    login = request.COOKIES.get('login', '')
    if not (login):
        # return HttpResponseRedirect('/travel/login')
        return None
    login_teacher = Teacher()
    if request.COOKIES.get('isTeacher', '') != '1':
        return None
    login_teacher.login = login
    login_teacher.name = request.COOKIES.get('name', '')
    login_teacher.name2 = request.COOKIES.get('name2', '')
    login_teacher.tel = request.COOKIES.get('tel', '')
    login_teacher.wechat = request.COOKIES.get('wechat', '')
    login_teacher.id = request.COOKIES.get('userid', '')
    login_teacher.isTeacher = request.COOKIES.get('isTeacher', '')
    return login_teacher

def checkCookie2(request):
    login = request.COOKIES.get('login', '')
    
    if not (login):
        # return HttpResponseRedirect('/travel/login')
        return None
    login_user = User()
    if request.COOKIES.get('isTeacher', '') == '1':

        return None
    try:
        login_user.login = login
        login_user.name = request.COOKIES.get('name', '')
        login_user.name2 = request.COOKIES.get('name2', '')
        login_user.tel = request.COOKIES.get('tel', '')
        login_user.c1wechat = request.COOKIES.get('wechat', '')
        login_user.id = request.COOKIES.get('userid', '')
        login_user.isTeacher = request.COOKIES.get('isTeacher', '')

    except Exception as e:
        print(e)
    return login_user


#TZName=None：Beijing时区
#TZName=UTC：0时区
def getDateNow(TZName=None):
    timeNow = None
    if not TZName:
        timeNow = datetime.datetime.fromtimestamp(mktime(time.localtime()))
    else:
        if TZName == 'UTC':
            now = int(time.time())
            timeNow = datetime.datetime.utcfromtimestamp(now)
        else:
            # get the standard UTC time
            UTC = pytz.utc
# it will get the time zone
# of the specified location
            IST = pytz.timezone(TZName)
            timeNow = datetime.datetime.now(IST)
# print the date and time in
# standard format


    return timeNow

def getWeekFirstDay(firstDay):
    if not firstDay:
        now = getDateNow()
        weekday = now.weekday()
        #print 'today is the No.' + str(weekday) + ' day of this week'
        #firstDay = weekday + 1
        firstDay = now - datetime.timedelta(days=weekday)
        firstDay = datetime.datetime.strptime(firstDay.strftime("%Y-%m-%d")+" 00:00:00","%Y-%m-%d %H:%M:%S")


    firstDay = firstDay.replace(hour=0)
    firstDay = firstDay.replace(minute=0)
    firstDay = firstDay.replace(second=0)
    firstDay = firstDay.replace(microsecond=0)

    lastDay = firstDay + datetime.timedelta(days=6)
    lastWeekFirstDay = firstDay + datetime.timedelta(days=-7)
    nextWeekFirstDay = firstDay + datetime.timedelta(days=7)

    return firstDay,lastDay,lastWeekFirstDay,nextWeekFirstDay

def getTimeZone(city):
    try:
        a = GeoNames(username='patchli')
        location = a.geocode(query=city)
        return a.reverse_timezone((location.latitude,location.longitude))
    except Exception as e:
        print(e)




# use your local timezone name here
# NOTE: pytz.reference.LocalTimezone() would produce wrong result here

## You could use `tzlocal` module to get local timezone on Unix and Win32
# from tzlocal import get_localzone # $ pip install tzlocal

# # get local timezone
# local_tz = get_localzone()

def  local_to_utc(localTimeStr,localTimezone):
    local = pytz.timezone (localTimezone)
    naive = datetime.datetime.strptime (localTimeStr, "%Y-%m-%d %H:%M:%S")
    local_dt = local.localize(naive, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt

def utc_to_local(utc_dt,timezone):

    if not timezone:
        timezone = 'Asia/Shanghai'

    local_tz = pytz.timezone(timezone)
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt) # .normalize might be unnecessary

def userCoursePlan(weeks = None):

    classrooms = Classroom.objects.filter(users__ne=None).order_by("lessonWeekday","lessonTime")  # @UndefinedVariable
    userCourse = {} #userId:courseNo pairs
    courses = {}
    j = 0
    if not weeks:
        weeks = 1
    temp0 = []

    for week in range(weeks+1):

        if week > 0:
            for c in classrooms:
                c2=Classroom()
                c2.code = str(week) + '-' + str(c.lessonWeekday)+'-'+c.lessonTime
                c2.lessonWeekday = c.lessonWeekday
                c2.lessonTime = c.lessonTime
                users = []
                for u in c.users:
                    u2 = User()
                    u2.name = u.name
                    u2.namw2 = u.name2
                    u2.c2email = str(week)+'-'+str(u.id)
                    u2.c1email = str(u.id)
                    users.append(u2)
                c2.users = users
                temp0.append(c2)

    for c in temp0:
        j = j + 1 #周期内上课顺序号
        temp = [] # all identical courseNos
        cn = 0

        for u in c.users:
            try:
                courseNos = userCourse[str(u.c1email)]
                list = courseNos.split('-')
                for l in list:
                    if int(l) > 0 and int(l) not in temp: #  put courseNo in temp list, if it not in temp list
                        temp.append(int(l))
            except:
                err = 1
        try:
            ttt = sorted(temp) # sort courseNo list
            i = 0
            for t in ttt:
                i = i + 1
                if t > i:
                    cn = i #找到未使用的课程编号，作为当前可用课程编号，退出循环
                    break
            if cn == 0:#如果当前课程编号为0，给值
                #print len(ttt)
                if len(ttt) == 0:
                    cn = 1
                else:
                    cn = len(ttt)+1
        except:
            cn = 1
       #print c.code + '-' + str(cn)
        for u in c.users:
            #print str(j) + '--' + str(len(c.users)) + '-cn-' + str(cn)
            pre = ''
            try:
                pre = userCourse[str(u.c1email)]
            except:
                pre = ''
            if pre == '':
                userCourse[str(u.c1email)] = str(cn) #set this course‘s courseNo as cn
            else:
                userCourse[str(u.c1email)] = pre + '-' + str(cn) #set this course‘s courseNo as cn
        #print c.code
        courses[c.code] = cn #当前时间的课程标号设为cn
    #print userCourse
    return courses

def removeComment():
    file = open("/Users/patch/Documents/project/patchclass/station.json",'r')
    file2 = open("/Users/patch/Documents/project/patchclass/station2.json",'a')
    lines = file.readlines()
    for line in lines:
        if line.find('/*') == -1:
            file2.writelines([line])
    print('DONE')
    return

if __name__ == "__main__":
    #print str2md5('jieli360')
    #getDateNow('Asia/Shanghai')
    #getDateNow()
    #getDateNow('UTC')
    #getDateNow('America/Phoenix')
    #getDateNow('Europe/Berlin')
    #getDateNow('Asia/Hong_Kong')
    #getTimeZone('Beijing')
    removeComment()
