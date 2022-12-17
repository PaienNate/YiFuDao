# coding:utf-8
import functools
import os
import threading
import time

import flask
import schedule as schedule
from flask import Flask, request, render_template, session, g, flash
from werkzeug.utils import redirect

import maodous

# Create a flask app of the specified name
import models
from maodous.authenticationData import User
from views.Auth import LoginForm
from yifudao.YiFuDao_Puncher import YiFuDao_Puncher
from yifudao.default_data import *
from utils.dingding_bot import DingDingBot
from utils.pushplus import PushPlus
from utils.smtp_sender import ErrorEmail
from utils.time_util import datetime_2string
from yifudao.punch_in_data_generator import punch_in_data_generator

from flask_login import LoginManager, login_required

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'

app = Flask(__name__)
login_manager.init_app(app)
# 返回凑合能用就行
from flask_login import current_user, login_user, logout_user

app.config['SECRET_KEY'] = 'CAONIMASHABIWANYI'
app.config['TESTING'] = False


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        # flash('已成功登录', FlashCategories.warning)
        return redirect('/list/')
    else:
        emsg = None
        form = LoginForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            # user_info = User.query.get(username)  # 从数据库中查找用户记录
            user_info = User.get_by_username(username)  # 从数据库中查找用户记录
            if user_info is None:
                emsg = "用户名有误!"
            else:
                user = user_info  # 创建用户实体
                if user.verify_password(password):
                    login_user(user)
                    return redirect('/list/')
                else:
                    emsg = "密码有误!"
        return render_template("login.html", form=form, emsg=emsg)


@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return redirect('/login/')


# When you go to localhost:PORT in your browser, this code will run
# Port is likely 5000, unless otherwise set.

@login_manager.user_loader
def load_user(user_id):
    return User.get(int(user_id))


@app.route('/list/')
@login_required
def userlist():
    # 显示用户列表
    userlist = models.get(models.Viewer)
    print('userlist:%s' % userlist)
    return render_template('list.html', userlist=userlist)



@app.route('/update/')
@login_required
def update():
    id = request.args.get('id')
    user = models.getOne(id)
    print('update:%s' % user)
    return render_template('update.html', user=user)



@app.route('/updateaction/', methods=['POST'])
@login_required
def updateaction():
    params = request.args if request.method == 'GET' else request.form
    id = params.get('id')
    token = params.get('token')
    name = params.get('name')
    email = params.get('email')
    data = params.get('data')
    need_daka = params.get('need_daka')
    viewer = models.Viewer(id=id, token=token, name=name, email=email, data=data, need_daka=need_daka)
    models.update(viewer)
    return redirect('/list/')



@app.route('/add/')
@login_required
def add():
    return render_template('add.html')



@app.route('/addaction/', methods=['POST'])
@login_required
def addaction():
    params = request.args if request.method == 'GET' else request.form
    # 添加
    token = params.get('token')
    name = params.get('name')
    email = params.get('email')
    data = params.get('data')
    need_daka = params.get('need_daka')
    viewer = models.Viewer(token=token, name=name, email=email, data=data, need_daka=need_daka)
    models.save(viewer)
    return redirect('/list/')


@app.route('/getNewLoc/')
@login_required
def getnewlocation():
    params = request.args if request.method == 'GET' else request.form
    # 添加
    id = params.get('id')
    mine = models.getOne(id)
    punch = punch_in_data_generator(mine.token)
    return punch.new  # redirect('/list/')



@app.route('/daka/')
@login_required
def mydaka():
    return render_template('daka.html', userlist=daka())


@app.route('/delete/')
@login_required
def delete():
    id = request.args.get('id')
    models.delete(id)
    return redirect('/list/')


def daka():
    accessDict = {}
    accessSend = {}
    accessLoc = {}
    accessNeed = {}
    # 添加返回值
    myreturn = {}
    # 使用flask的对应，获取到对应的Viewer
    userlist = models.get(models.Viewer)
    for accessman in userlist:
        # 获得的是个元组的集合，对这个集合进行处理
        id = accessman.id
        name = accessman.name
        token = accessman.token
        email = accessman.email
        data = accessman.data
        print(id)
        print(name)
        need_daka = accessman.need_daka
        # 由于0号是ID位，所以从1号开始,首先获取姓名
        accessDict[token] = name
        # 获取对应的邮箱
        accessSend[token] = email
        # 获取对应的data数据信息，注意要转换为对应格式
        accessLoc[token] = eval(data)
        accessNeed[token] = need_daka

    for accessToken in accessDict.keys():
        if accessNeed[accessToken] == 1:
            puncher = YiFuDao_Puncher(accessToken, accessDict[accessToken], accessLoc[accessToken])
            # 使用accessLoc的对应获取打卡位置
            locationdict = accessLoc[accessToken]["answerInfoList"][1]["location"]
            mylocation = locationdict["province"] + locationdict["city"] + locationdict["street"] + locationdict[
                "area"] + \
                         locationdict["address"]
            title = "奕辅导健康打卡通知：{}".format(puncher.puncher_status)
            text = """
                    *** 奕辅导健康打卡通知 ***
                    时间：{}
                    打卡情况：{}，请检查打卡位置是否正确： 打卡位置:{},
                    """.format(datetime_2string(), puncher.puncher_status, mylocation)
            myreturn[accessDict[accessToken]] = puncher.puncher_status + "打卡位置" + mylocation
            if notify == "DingDing":
                notifier = DingDingBot(dingding_access_token, dingding_secret)
                notifier.set_msg(title, text)
                notifier.send()
            elif notify == "Mail":
                mail_receiver = []
                mail_receiver.append(accessSend[accessToken])
                ee = ErrorEmail(mail_sender, mail_auth_code, mail_receiver)
                msg = ee.theme_content(title, text)
                ee.send_message(mail_smtp_link, mail_smtp_port, msg)
            elif notify == "PushPlus":
                notifier = PushPlus.send(pushplus_token, title, text, "markdown")
        else:
            title = "奕辅导健康打卡通知：关闭打卡!"
            text = """
                    *** 奕辅导健康打卡通知 ***
                    时间：{}
                    打卡情况：{}，请检查打卡位置是否正确： 打卡位置:{},
                    """.format(datetime_2string(), "您的打卡已经被关闭!", "打卡位置不检测！")
            myreturn[accessDict[accessToken]] = "您的打卡已经被关闭!"
            mail_receiver = []
            mail_receiver.append(accessSend[accessToken])
            ee = ErrorEmail(mail_sender, mail_auth_code, mail_receiver)
            msg = ee.theme_content(title, text)
            ee.send_message(mail_smtp_link, mail_smtp_port, msg)
    return myreturn


def task_thread():
    while True:
        print("等待打卡进度中……")
        schedule.run_pending()
        time.sleep(1)


# On startup, if this is main, this section of code will run
if __name__ == "__main__":
    # 主定时
    myjob0 = schedule.every().day.at("18:05").do(daka)
    # 备用定时
    myjob = schedule.every().day.at("18:10").do(daka)
    # 备用定时2
    myjob2 = schedule.every().day.at("18:20").do(daka)
    # 启动
    threading.Thread(target=task_thread).start()
    app.config['JSON_AS_ASCII'] = False
    app.config.update(RESTFUL_JSON=dict(ensure_ascii=False))
    # Get the port to liston on. By default, it will listen on 5000
    # This uses an environmental variable to figure out if another port is requested
    port = int(os.environ.get("PORT", 5000))
    # Tell the Flask app to listen on the specified port and serve requests
    app.run(host='0.0.0.0', port=port)
