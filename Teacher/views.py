# -*- coding:utf-8 -*-
'''
Created on Aug 16, 2020

@author: patch
'''
import json,time,datetime
from Tool import constant,models,util, batch
from django import forms
from django.views.decorators.csrf import  csrf_exempt
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render#,render_to_response
from django.utils.dateparse import parse_datetime
from Tool.models import Teacher, Classroom, User,Lesson, Course, UserLesson
from mongoengine.queryset.visitor import Q

# Create your views here.

def swipe(request):
    login_teacher = util.checkCookie(request)
    id = request.GET.get('id')
    if not id == 'patch':
        return HttpResponseRedirect('/login')
    page = request.GET.get('page')
    return render(request, 'swipe.html', {"page":page})

def horse(request):
    login_teacher = util.checkCookie(request)
    id = request.GET.get('id')
    if not id == 'patch':
        return HttpResponseRedirect('/login')
    page = request.GET.get('page')
    return render(request, 'horse.html', {"page":page})

class UserLoginForm(forms.Form):
    username = forms.CharField(label='登录名', max_length=100,
                               widget=forms.TextInput(attrs={'class': 'form-control','autofocus':'autofocus'}))
    password = forms.CharField(label='密码', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

@csrf_exempt
def login(request):
    isTeacher = False
    if request.method == "POST":
        uf = UserLoginForm(request.POST)

        if uf.is_valid():
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            openId = request.POST.get("openId")


            res = {"error": 0, "msg": "OK"}
            password_md5 = util.str2md5(password)
            if password_md5 == None:
                res = {"error": 1, "msg": "非法字符"}
            username = username.lower()

            user = None

            users = []
            users = Teacher.objects.filter(login__exact=username).filter(pw__exact=password_md5)  # @UndefinedVariable
            try:
                user = users.first()
                if user.status == -1:
                    res = {"error": 1, "msg": "已离职"}
                else:
                    isTeacher = True
            except:
                users = User.objects.filter(login__exact=username).filter(pw__exact=password_md5)  # @UndefinedVariable
                try:
                    user = users.first()
                    if user.status == -1:
                        res = {"error": 1, "msg": "已注销"}
                except:
                    res = {"error": 1, "msg": "用户名密码错误"}


            res_login = res
            if res_login["error"] == 0 and isTeacher:

                response = HttpResponseRedirect('/Teacher/lessonPlan')
                response.set_cookie('isTeacher', '1')
                response.set_cookie('login', user.login.lower())
                response.set_cookie('userid', user.id)
                response.set_cookie('name', user.name)
                response.set_cookie('name2', user.name2)
                response.set_cookie('wechat',user.wechat)
                response.set_cookie('tel',user.tel)

                return response
            elif res_login["error"] == 0:
                response = HttpResponseRedirect('/User/myRefers')
                response.set_cookie('login',user.login)
                response.set_cookie('userid', user.id)
                response.set_cookie('name', user.name)
                response.set_cookie('name2', user.name2)
                response.set_cookie('wechat',user.wechat)
                response.set_cookie('tel',user.tel)
                return response
            else:
                response = HttpResponseRedirect('/login?wrongLogin=1')
                return response
                #return render('login.html', {'msg': res_login["msg"], 'uf': uf})
    else:
        uf = UserLoginForm()
    return render(request, 'login.html', {'uf': uf,'addr':request.META['HTTP_HOST']})

def editClass(request):
    login_teacher = util.checkCookie(request)
    if not (login_teacher):
        return HttpResponseRedirect('/login')
    classroom = None
    classroomId = request.GET.get('classroomId')
    try:
        classroom = Classroom.objects.get(id=classroomId)  # @UndefinedVariable
    except:
        classroom = None

    query = Q(status=1)
    if classroom:
        for u in classroom.users:
            query = query&Q(id__ne=u.id)
    #除了本班学生以外所有可选学生
    students = User.objects.filter(query).order_by('name')  # @UndefinedVariable

    classStudents = None
    if classroom:
        classStudents = classroom.users
    week_list = range(1, 8)
    teachers = Teacher.objects.all()  # @UndefinedVariable
    lans = constant.LAN
    print(lans)
    return render(request, 'editClass.html', {"login_teacher":login_teacher,"classroom":classroom,
                                              "students":students,"classStudents":classStudents,
                                              'week_list':week_list,"teachers":teachers,"lans":lans,
                                              "searchDay":request.GET.get("searchDay")})
@csrf_exempt
def api_editClass(request):
    login_teacher = util.checkCookie(request)
    if not (login_teacher):
        return HttpResponseRedirect('/login')

    classroomId = request.POST.get('classroomId')
    studentIds = request.POST.get('studentIds')
    teacherId = request.POST.get('teacherId')
    lan = request.POST.get('lan')
    lessonWeekday = request.POST.get('lessonWeekday')
    lessonTime = request.POST.get('lessonTime')

    res = {"error": 0, "msg": "OK"}
    classroom = None
    try:
        classroom = Classroom.objects.get(id=classroomId)  # @UndefinedVariable
    except Exception as e:
        print(e)
        classroom = None

    if not classroom:
        classroom = Classroom()
    teacher = None
    try:
        teacher = Teacher.objects.get(id=teacherId)  # @UndefinedVariable
    except:
        teacher = None

    classroom.teacher = teacher
    classroom.lan = lan
    classroom.lessonWeekday = lessonWeekday
    classroom.lessonTime = lessonTime

    students = []
    student_oid_list = json.loads(studentIds)
    for student_oid in student_oid_list:
        try:
            student = User.objects.get(id=student_oid)  # @UndefinedVariable
            student.inClass = 1
            student.save()
            students.append(student)
        except Exception as e:
            print(e)
            res = {"error": 1, "msg": str(e)}
            return util.JSONResponse(json.dumps(res, ensure_ascii=False))
    oldclass = classroom.users
    classroom.users = students
    classroom.save()
    for o in oldclass:
        stillIn = False
        for s in students:
            if o.id == s.id:
                stillIn = True
                break;
        if not stillIn:
            query = Q(users__contains=o.id)
            has = Classroom.objects.filter(query)  # @UndefinedVariable
            if len(has) == 0:
                o.inClass = 0
                o.save()

    return util.JSONResponse(json.dumps(res, ensure_ascii=False))


#展示一周每天课程安排，左右滑动展示前后一天
def lessonPlan(request):
    #batch.changeThemeToList()
    login_teacher = util.checkCookie(request)
    if not (login_teacher):
        return HttpResponseRedirect('/login')
    searchDayStr = request.GET.get("searchDay")
    searchDay = None
    try:
        searchDay = datetime.datetime.strptime(searchDayStr,"%Y%m%d")
    except:
        searchDay = None

    begin,end,last,next = util.getWeekFirstDay(searchDay)
    end = end.replace(hour=23)
    end = end.replace(minute=59)
    end = end.replace(second=59)
    isThisWeek = True

    query = Q(teacher=login_teacher.id)&Q(users__ne=None)
    lessonPlans = Classroom.objects.filter(query).order_by('lessonWeekday','lessonTime')  # @UndefinedVariable
    all = []

    lastDay = None
    temp = []
    i = 0
    date = None
    courses = util.userCoursePlan(1)
    print(courses)
    for c in lessonPlans:
        if lastDay != c.lessonWeekday:
            date = begin + datetime.timedelta(days=i)
            strd = datetime.datetime.strftime(date,"%Y-%m-%d")
            date = parse_datetime(strd + "T" + c.lessonTime + ":0+08:00")
            #date = parse_datetime('2020-09-19T10:00:0+08:00')

            i = i + 1
            try:
                if temp and len(temp) >0:
                    all.append(temp)
                    temp = []
            except Exception as e:
                print(e)
            lastDay = c.lessonWeekday

        c.date = date#util.utc_to_local(date, None)

        lesson = None
        try:

            query = Q(classroom=c.id)&Q(lessonDate__gte=begin)&Q(lessonDate__lte=end)

            lessons = Lesson.objects.filter(query)  # @UndefinedVariable

            if len(lessons) > 0:
                lesson = lessons[0]
                lesson.lessonDate = util.utc_to_local(lesson.lessonDate, None)

            c.lesson = lesson

        except Exception as e:
            print(e)
            c.lesson = Lesson()
        c.code = '1-' + str(c.lessonWeekday)+'-'+c.lessonTime
        c.courseNo = courses[c.code]

        temp.append(c)

    all.append(temp)
#
    return render(request, 'lessonPlan.html', {
        "login_teacher":login_teacher,
        "lessonPlans":all,
        "last":last,"next":next,
        "begin":begin,"end":end,"searchDay":searchDayStr,
        "isThisWeek":isThisWeek})

#上课签到，涉及Lesson和UserLesson两个表，Lesson记录上课内容和时间信息，UserLesson记录每个学生出勤
def lessonCheckin(request):
    login_teacher = util.checkCookie(request)
    if not (login_teacher):
        return HttpResponseRedirect('/login')
    lessonId = request.GET.get("lessonId")
    lesson = None
    course = None
    try:
        lesson = Lesson.objects.get(id=lessonId)  # @UndefinedVariable
        #lesson.lessonDate = util.utc_to_local(lesson.lessonDate, None)
        course = lesson.course
    except:
        lesson = None
    courseId = request.GET.get("courseId")
    if courseId:
        try:
            course = Course.objects.get(id=courseId)  # @UndefinedVariable
            if lesson:
                lesson.course = course
        except:
            course = None

    classroomId = request.GET.get("classroomId")
    classroom = None

    try:
        classroom = Classroom.objects.get(id=classroomId)  # @UndefinedVariable
    except Exception as e:
        return render(request, 'lessonCheckin.html', {"login_teacher":login_teacher,"err":str(e)})

    courses = Course.objects.all()  # @UndefinedVariable
    temp = []
    for c in courses:
        c.content = ''#'c.content.replace('\n',' ')
        temp.append(c)

    lessonDate = request.GET.get("lessonDate")
    userLessons = None
    users = []
    if lesson:
        query = Q(lesson=lesson.id)
        userLessons = UserLesson.objects.filter(query).order_by("user")  # @UndefinedVariable
        for u in classroom.users:
            for ul in userLessons:
                if u.id == ul.user.id:
                    u.lesson = ul
                    break
            users.append(u)
    return render(request, 'lessonCheckin.html', {"login_teacher":login_teacher,"lesson":lesson,"course":course,
                                                  "classroom":classroom,"courses":temp,"lessonDate":lessonDate,
                                                  "users":users})


#删除某一安排错的课
@csrf_exempt
def api_deleteLesson(request):
    login_teacher = util.checkCookie(request)
    if not (login_teacher):
        return HttpResponseRedirect('/login')

    lessonId = request.POST.get("lessonId")
    lesson = None
    try:
        lesson = Lesson.objects.get(id=lessonId)  # @UndefinedVariable
        lesson.delete()
        res = {"error": 0, "msg": "OK"}
    except Exception as e:
        res = {"error": 1, "msg": e.message()}

    return util.JSONResponse(json.dumps(res, ensure_ascii=False))

#课程安排和签到
@csrf_exempt
def api_lessonCheckin(request):
    login_teacher = util.checkCookie(request)
    memo = request.POST.get("memo")
    if not (login_teacher):
        return HttpResponseRedirect('/login')

    lessonId = request.POST.get("lessonId")
    lesson = None
    try:
        lesson = Lesson.objects.get(id=lessonId)  # @UndefinedVariable
    except:
        lesson = Lesson()
        classroomId = request.POST.get("classroomId")
        classroom = None
        try:
            classroom = Classroom.objects.get(id=classroomId)  # @UndefinedVariable
        except Exception as e:
            res = {"error": 1, "msg": "教室有误"}
            return util.JSONResponse(json.dumps(res, ensure_ascii=False))
        lesson.classroom = classroom

        teacherId = login_teacher.id#request.POST.get("teacherId")
        teacher = None
        try:
            teacher = Teacher.objects.get(id=teacherId)  # @UndefinedVariable
        except Exception as e:
            res = {"error": 1, "msg": "老师有误"}
            return util.JSONResponse(json.dumps(res, ensure_ascii=False))
        lesson.teacher = teacher

        ld = request.POST.get('lessonDate')
        lessonDate = None
        try:
            ld = ld + ":0+08:00"
            lessonDate = parse_datetime(ld)
            lesson.lessonDate = lessonDate
        except:
            res = {"error": 1, "msg": "日期有误"}
            return util.JSONResponse(json.dumps(res, ensure_ascii=False))

    courseId = request.POST.get("courseId")
    course = None
    lesson.memo = memo
    try:
            course = Course.objects.get(id=courseId)  # @UndefinedVariable
            lesson.course = course
    except Exception as e:
            res = {"error": 1, "msg": "课程有误"}
            return util.JSONResponse(json.dumps(res, ensure_ascii=False))

    lesson.course = course

    lesson.save()

    dataStr = request.POST.get("data")
    data = dataStr.split(';')
    exist = UserLesson.objects.filter(lesson=lesson.id)#delete @UndefinedVariable
    for e in exist:
        e.delete()
    for udataStr in data:
        if udataStr:
            ul = UserLesson()
            ul.lesson = lesson
            ul.lessonDate = lesson.lessonDate
            udata = udataStr.split(',')
            if udata[0]:
                try:
                    ul.user = User.objects.get(id=udata[0])  # @UndefinedVariable
                except Exception as e:
                    res = {"error": 1, "msg": str(e)}
                    return util.JSONResponse(json.dumps(res, ensure_ascii=False))

            if udata[1]:
                theme = udata[1].split('_')
                temp = []
                for t in theme:
                    if t:
                        temp.append(t)
                ul.theme = temp
            if udata[2]:
                extention = udata[2].split('_')
                temp = []
                for ex in extention:
                    if ex:
                        temp.append(ex)
                ul.extention = temp
            if udata[3]:
                skill = udata[3].split('_')
                temp = []
                for s in skill:
                    if s:
                        temp.append(s)
                ul.skill = temp
            if udata[4]:
                ability = udata[4].split('_')
                temp = []
                for a in ability:
                    if a:
                        temp.append(a)
                ul.ability = temp
            if udata[5]:
                ul.work = udata[5]
            if udata[6]:
                ul.memo = udata[6]
            if udata[7]:
                ul.media = udata[7]
            if ul.user:
                ul.save()
                query = Q(user=ul.user.id)
                lessons = UserLesson.objects.filter(query)  # @UndefinedVariable
                try:
                    ul.user.lessons = len(lessons)
                    ul.user.save()
                except:
                    ul.user.lessons = 0
    res = {"error": 0, "msg": "OK"}
    return util.JSONResponse(json.dumps(res, ensure_ascii=False))


def courseList(request):
    login_teacher = util.checkCookie(request)
    if not (login_teacher):
        return HttpResponseRedirect('/login')
    query = Q(lan__ne=None)
    #courses = Course.objects.all().order_by("lan,level")  # @UndefinedVariable
    courses = Course.objects.all()  # @UndefinedVariable
   # for c in courses:

       # c.save()
    list = []
    temp = []
    lastLan = None
    lastLevel = -1
    courses = Course.objects.filter(query).order_by("lan","level")  # @UndefinedVariable
    for course in courses:
        try:
            course.lan = course.lan[0]
        except:
            course.lan = None
            print(1)
        if lastLan != None and course.lan != lastLan:
            list.append(temp)
            print('change lan')
            temp = []
            lastLevel = -1
            lastLan = course.lan
        elif lastLevel != -1 and course.level != lastLevel:
            list.append(temp)
            print('change level')
            temp = []
            lastLevel = course.level
        lastLan = course.lan
        lastLevel = course.level
        temp.append(course)
    list.append(temp)
    print('change end')
    return render(request, 'courseList.html', {"login_teacher":login_teacher,"list":list})


def courseEdit(request):
    login_teacher = util.checkCookie(request)
    if not (login_teacher):
        return HttpResponseRedirect('/login')
    courseId = request.GET.get("courseId")
    course = None
    try:
        course = Course.objects.get(id=courseId)  # @UndefinedVariable
    except:
        course = None
    return render(request, 'courseEdit.html', {"login_teacher":login_teacher,"course":course,
                                               "lan":constant.LAN,"theme":constant.THEME,
                                               "skill":constant.SKILL,"sensor":constant.SENSOR,
                                               "output":constant.OUTPUT,"extention":constant.EXTENTION,
                                               "ability":constant.ABILITY
                                               })


#课程安排和签到
@csrf_exempt
def api_courseEdit(request):
    login_teacher = util.checkCookie(request)
    if not (login_teacher):
        return HttpResponseRedirect('/login')
    courseId = request.POST.get("courseId")
    name = request.POST.get("name")
    content = request.POST.get("content")
    skill = request.POST.get("skill")
    ability = request.POST.get("ability")
    theme =  request.POST.get("theme")
    extention =  request.POST.get("extention")
    output =  request.POST.get("output")
    lan =  request.POST.get("lan")
    sensor =  request.POST.get("sensor")


    level =  request.POST.get("level")

    try:
        skill = json.loads(skill)
    except Exception as e:
        print(e)

    try:
        theme = json.loads(theme)
    except Exception as e:
        print(e)

    try:
        lan = json.loads(lan)
    except Exception as e:
        print(e)

    try:
        sensor = json.loads(sensor)
    except Exception as e:
        print(e)

    try:
        output = json.loads(output)
    except Exception as e:
        print(e)


    try:
        level = int(level)

    except Exception as e:
        print(e)

    try:
        ability = json.loads(ability)

    except Exception as e:
        print(e)
        ability = None
    try:
        extention = json.loads(extention)
    except Exception as e:
        print(e)
        extention = None
    course = None
    try:
        course = Course.objects.get(id=courseId)  # @UndefinedVariable
    except:
        course = Course()

    course.name = name
    course.content = content
    course.theme = theme
    course.skill = skill
    course.ability = ability
    course.level = level

    course.extention = extention
    course.lan = lan
    course.sensor = sensor
    course.output = output

    course.save()

    res = {"error": 0, "msg": "OK"}
    return util.JSONResponse(json.dumps(res, ensure_ascii=False))

def userCoursePlan(request):
    login_teacher = util.checkCookie(request)
    if not (login_teacher):
        return HttpResponseRedirect('/login')
    classrooms = Classroom.objects.filter(users__ne=None).order_by("lessonWeekday","lessonTime")  # @UndefinedVariable
    userCourse = {}
    courses = {}
    j = 0
    for c in classrooms:
        j = j + 1
        temp = []
        cn = 0

        for u in c.users:
            try:
                courseNo = userCourse[str(u.id)]
                #print (courseNo in temp)
                if courseNo > 0 and courseNo not in temp:
                    temp.append(courseNo)
            except:
                err = 1
        try:
            ttt = sorted(temp)
            i = 0
            for t in ttt:
                i = i + 1
                if t > i:
                    cn = i
                    break
            if cn == 0:
                if len(ttt) == 0:
                    cn = 1
                else:
                    cn = len(ttt)+1
        except:
            cn = 1
        for u in c.users:
            #print str(j) + '--' + str(len(c.users)) + '-cn-' + str(cn)
            userCourse[str(u.id)] = cn
        courses[str(c.lessonWeekday)+'-'+c.lessonTime] = cn


    ks = sorted(courses.keys())
    #for k in ks:
     #   print k + '-' + str(courses[k])
    return render(request, 'userCoursePlan.html', {"login_teacher":login_teacher,"courses":userCourse})

def userLessonSkill(request):
    login_teacher = util.checkCookie(request)
    if not (login_teacher):
        return HttpResponseRedirect('/login')
    userLessons = UserLesson.objects.filter()  # @UndefinedVariable
    skill = {}
    theme = {}
    ability = {}
    j = 0
    for c in userLessons:
        j = j + 1
        temp = []
        for s in c.skill:
            try:
                skill[s] = skill[s] + 1
            except:
                skill[s] = 1
    return render(request, 'userLessonSkill.html', {"login_teacher":login_teacher,"skill":skill})
