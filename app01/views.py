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
    rooms = models.Room.objects.all()
    time_choices = models.Book.time_choice
    return render(request, 'index.html', {'time_choices': time_choices})


def initBook(request):
    if request.method=='GET':
        user_id = request.session['user'].get('id')
        rooms = models.Room.objects.all()
        time_choices = models.Book.time_choice
        date = request.GET.get('date')
        date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        nowdate = datetime.datetime.now().date()
        if date >= nowdate:
            books = models.Book.objects.filter(date=date)
            print(books)
            book_dic = {}
            for book in books:
                if book.room_id in book_dic:
                    book_dic[book.room_id][book.time] = {'username': book.user.name, 'userid': book.user.id}
                else:
                    book_dic[book.room_id] = {book.time: {'username': book.user.name, 'userid': book.user.id}}
            data = []
            for room in rooms:
                tr = []
                tr.append({'text': room.name, 'attrs': {}})
                for tm in time_choices:
                    if room.id in book_dic and tm[0] in book_dic[room.id]:
                        if user_id == book_dic[room.id][tm[0]]['userid']:
                            td = {'text': book_dic[room.id][tm[0]]['username'],
                                  'attrs': {'roomid': room.id, 'tm': tm[0], 'class': "chosen"}}
                        else:
                            td = {'text': book_dic[room.id][tm[0]]['username'],
                                  'attrs': {'roomid': room.id, 'tm': tm[0], 'class': "chosen",'fk':'true'}}
                    else:
                        td = {'text': '', 'attrs': {'roomid': room.id, 'tm': tm[0]}}
                    tr.append(td)

                data.append(tr)
            reponse = {"data": data}
            print(data)

            return JsonResponse(reponse)

        else:
            raise Exception("只能预定今天或者以后的会议室")
    elif request.method=="POST":
        response = {'status': True, 'msg': None, 'data': None}
        try:
            print(123)
            date = request.POST.get('date')
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            nowdate = datetime.datetime.now().date()

            data=request.POST.get('data')
            data=json.loads(data)
            print(date)
            print(data)
            if date >= nowdate:
                #判断del和add中有没有重复
                for room_id in data.get("del"):
                    if room_id not  in data.get('add'):
                        continue
                    for tm in data['del'][room_id]:
                        if tm in data['add'][room_id]:
                            data['del'][room_id].remove(tm)
                            data['add'][room_id].remove(tm)

                #增加预定
                add_list=[]
                user_id=request.session['user'].get('id')
                for room_id,tm_list in data['add'].items():
                    for tm in tm_list:
                        book=models.Book(room_id=room_id,user_id=user_id,date=date,time=tm)
                        add_list.append(book)
                models.Book.objects.bulk_create(add_list)


                #取消预定
                from django.db.models import Q
                remove_books=Q()
                for room_id,tm_list in data['del'].items():
                    print(room_id,'-------')
                    for tm in tm_list:
                        print(tm,'******')
                        temp = Q()
                        temp.connector = 'AND'
                        temp.children.append(('user_id', user_id))
                        temp.children.append(('date', date))
                        temp.children.append(('room_id', room_id,))
                        temp.children.append(('time', tm,))

                        remove_books.add(temp, 'OR')

                if remove_books:
                    print(remove_books)
                    print(123)
                    models.Book.objects.filter(remove_books).delete()
            else:
                raise Exception("只能预定今天或者以后的会议室")
        except Exception as e:
            response['status']=False
            response['msg']=str(e)
        return JsonResponse(response)










