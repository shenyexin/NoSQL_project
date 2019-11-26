"""Movie_Order URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import pymongo
import random
import json
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect, HttpResponse

count = 0
strs = ''
mongodb = "*********"  # Mongodb服务器地址


def home(request):
    if request.method == 'GET':
        return render(request, 'home.html')
    else:
        nickname = request.POST.get('nickname')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        myclient = pymongo.MongoClient(mongodb, 27017)
        mydb = myclient.Movie
        mycol = mydb.user
        mydict = {"_id": phone, "password": password, "nickname": nickname, "benefit": 0, "money": 0}
        mycol.insert_one(mydict)
        return render(request, 'home.html')


def register(request):
    myclient = pymongo.MongoClient(mongodb, 27017)
    mydb = myclient.Movie
    mycol = mydb.user
    exist = []
    for field in mycol.find({}, {'_id': 1}):
        exist.append(field['_id'])
    lenth = exist.__len__()
    return render(request, 'register.html', {'exist': json.dumps(exist), 'lenth': lenth})


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        myclient = pymongo.MongoClient(mongodb, 27017)
        mydb = myclient.Movie
        mycol = mydb.user
        global user_phone, user_name, user_pwd, user_benefit, user_money
        for field in mycol.find({'_id': phone}):
            right = field['password']
            user_phone = field['_id']
            user_pwd = field['password']
            user_name = field['nickname']
            user_benefit = field['benefit']
            user_money = field['money']
            if right == password:
                return redirect('/movielist/?user=%s' % user_phone)
        return render(request, 'login.html', {'msg': "用户名或密码错误"})


def movielist(request):
    myclient = pymongo.MongoClient(mongodb, 27017)
    mydb = myclient.Movie
    mycol_movie = mydb.movie
    movie_list = []
    global strs
    strs=''
    for field in mycol_movie.find():
        movie_list.append(field)
    mycol_user = mydb.user
    global user_benefit
    if user_benefit == 0:
        user_benefit = round(random.uniform(2, 6), 1)
        mycol_user.update_one({"_id": user_phone}, {"$set": {"benefit": user_benefit}})
        return render(request, 'movielist.html', {'movie_list': movie_list, 'benefit': user_benefit})
    else:
        return render(request, 'movielist.html', {'movie_list': movie_list, 'benefit': 0})


def order(request):
    global title, count
    count = random.randint(0, 40)
    title = request.GET.get('title')
    myclient = pymongo.MongoClient(mongodb, 27017)
    mydb = myclient.Movie
    mycol = mydb.movie
    for x in mycol.find({"title": title}, {"_id": 0, "price": 1}):
        global price
        price = int(x['price'])
    movie_list = []
    for field in mycol.find({"title": title}):
        movie_list.append(field)
    return render(request, 'order.html', {'count': count, 'movie_list': movie_list[0]})


def pay(request):
    num = request.GET.get('num')
    if num == '':
        return redirect('/order/?title=%s' % title)
    else:
        num = int(num)
        if num > count:
            return redirect('/order/?title=%s' % title)
        else:
            riqi = request.GET.get('selected1')
            changci = request.GET.get('selected2')
            myselect = riqi + "-" + changci
            global total
            total = price * num - user_benefit
            return render(request, 'pay.html', {'total': total, 'benefit': user_benefit, 'title': title,
                                                'myselect': myselect, 'money': user_money})


def finish(request):
    myclient = pymongo.MongoClient(mongodb, 27017)
    mydb = myclient.Movie
    mycol = mydb.user
    mycol.update_one({'_id': user_phone}, {'$set': {'money': round(user_money - total, 1)}})
    mycol.update_one({'_id': user_phone}, {'$set': {'benefit': 0}})
    chars = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPLKJHGFDSAZXCVBNM1234567890'
    global strs
    strs = ''
    for i in range(12):
        key = random.randint(0, 61)
        s = chars[key]
        strs += s
    return render(request, 'finish.html', {'strs': strs})


def person(request):
    global user_phone, user_name, user_pwd, user_benefit, user_money
    myclient = pymongo.MongoClient(mongodb, 27017)
    mydb = myclient.Movie
    mycol = mydb.user
    for field in mycol.find({'_id': user_phone}):
        user_pwd = field['password']
        user_name = field['nickname']
        user_benefit = field['benefit']
        user_money = field['money']
    global strs
    if strs == '':
        return render(request, 'person.html', {'nickname': user_name, 'benefit': user_benefit,
                                               'money': user_money, 'code': "您尚未购票"})
    else:
        return render(request, 'person.html', {'nickname': user_name, 'benefit': user_benefit,
                                               'money': user_money, 'code': "您的取票码为：" + strs})


def add_money(request):
    addmoney = request.POST.get('addmoney')
    try:
        addmoney = int(addmoney)
    except Exception:
        return HttpResponse('No')
    if addmoney > 0:
        myclient = pymongo.MongoClient(mongodb, 27017)
        mydb = myclient.Movie
        mycol = mydb.user
        mycol.update_one({"_id": user_phone}, {"$set": {"money": round(addmoney + user_money, 1)}})
        return HttpResponse('OK')
    else:
        return HttpResponse('No')


def modify_pwd(request):
    new_pwd = request.POST.get("new_pwd")
    if len(new_pwd) > 0:
        myclient = pymongo.MongoClient(mongodb, 27017)
        mydb = myclient.Movie
        mycol = mydb.user
        print(new_pwd)
        print(user_phone)
        mycol.update_one({'_id': user_phone}, {"$set": {"password": new_pwd}})
        return HttpResponse("OK")
    else:
        return HttpResponse("No")


def log_off(request):
    confirm = request.POST.get("confirm")
    if confirm == '确认':
        myclient = pymongo.MongoClient(mongodb, 27017)
        mydb = myclient.Movie
        mycol = mydb.user
        mycol.delete_one({'_id': user_phone})
        return HttpResponse("OK")
    else:
        return HttpResponse("No")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('movielist/', movielist),
    path('login/', login),
    path('register/', register),
    path('order/', order),
    path('pay/', pay),
    path('finish/', finish),
    path('person/', person),
    path('add_money/', add_money),
    path('modift_pwd/', modify_pwd),
    path('log_off/', log_off)

]
