"""PatchClass URL Configuration


"""
from django.conf.urls import url,include
from User.views import *


urlpatterns = [
    url(r'^profile$', profile,name="profile"),
    url(r'^work$', work,name="work"),
    url(r'^userList$', userList,name="userList"),
    url(r'^userEdit$', userEdit,name="userEdit"),
    url(r'^api_userEdit$', api_userEdit,name="api_userEdit"),
    url(r'^userSkill$', userSkill,name="userSkill"),
    url(r'^index$', index,name="index"),
    url(r'^pay$', pay,name="pay"),
    url(r'^myRefers$', myRefers,name="myRefers"),
    url(r'^api_pay$', api_pay,name="api_pay"),
    url(r'^changePW$', changePW,name="changePW"),
    url(r'^api_changePW$', api_changePW,name="api_changePW")


]
app_name = 'User'
