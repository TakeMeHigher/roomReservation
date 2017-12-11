from django.shortcuts import render, HttpResponse, redirect
from app01 import models
from django.http import JsonResponse
import datetime
import json
import time


#   滑动验证码
from app01.geetest import GeetestLib

pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"
mobile_geetest_id = "7c25da6fe21944cfe507d2f9876775a9"
mobile_geetest_key = "f5883f4ee3bd4fa8caec67941de1b903"


def pcgetcaptcha(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)


# 滑动验证码登录
def pcajax_validate(request):
    if request.method == "POST":
        login_response = {"is_login": False, "error_msg": None}
        #  验证验证码
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        # 扩充 验证用户名密码
        if result:
            username = request.POST.get("username")
            password = request.POST.get("password")

            user = models.UserInfo.objects.filter(name=username, pwd=password).first()
            if user:
                login_response["is_login"] = True
                request.session['user'] = {"id": user.id, "name": username}

            else:
                login_response["error_msg"] = "username or password error"

        else:
            login_response["error_msg"] = "验证码错误"

        return HttpResponse(json.dumps(login_response))

    return HttpResponse("error")


def login(request):
    return render(request, 'login.html')


def index(request):
    rooms=models.Room.objects.all()
    time_choices=models.Book.time_choice
    return render(request,'index.html',{'rooms':rooms,'time_choices':time_choices})


def initBook(request):
    rooms = models.Room.objects.all()
    time_choices = models.Book.time_choice
    date=request.GET.get('date')
    date=datetime.datetime.strptime(date, '%Y-%m-%d').date()
    nowdate=datetime.datetime.now().date()
    if date>=nowdate:
        books=models.Book.objects.filter(date=date)
        print(books)
        book_dic={}
        for book in books:
            if book.room_id in book_dic:
                book_dic[book.room_id][book.time]={'username':book.user.name,'userid':book.user.id}
            else:
                book_dic[book.room_id]={book.time:{'username':book.user.name,'userid':book.user.id}}
        data=[]

        for room in rooms:
            tr = []
            tr.append({'text':room.name,'attrs':{}})
            for tm in time_choices:
                if room.id in book_dic and tm[0] in book_dic[room.id]:
                    td={'text':book_dic[room.id][tm[0]]['username'],'attrs':{'roomid':room.id,'tm':tm[0],'class':"chosen"}}
                else:
                    td={'text':'','attrs':{'roomid':room.id,'tm':tm[0]}}
                tr.append(td)

            data.append(tr)
        reponse={"data":data}
        print(data)
        time.sleep(5)
        return JsonResponse(reponse)

    else:
        raise Exception("只能预定今天或者以后的会议室")

