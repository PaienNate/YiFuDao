# -*- encoding:utf-8 -*-
import json
import time

import requests

import default_data
from YiFuDao_Puncher import YiFuDao_Puncher
from default_data import *
from utils.dingding_bot import DingDingBot
from utils.pushplus import PushPlus
from utils.smtp_sender import ErrorEmail
from utils.time_util import datetime_2string
import sqlite3
import schedule

# 连接数据库
conn = sqlite3.connect('yifudao.db')
cur = conn.cursor()
# 使用创建的游标
getall = "select * from punch"
# 运行时直接执行它
cur.execute(getall)
myget = cur.fetchall()


def get_user_name(self, accessToken):
    try:
        base_url = "https://yfd.ly-sky.com"
        header = {
            "accessToken": accessToken,
            "userAuthType": "MS"
        }
        url = '/ly-ms/application/api/st/mine/getUserInfo'
        header["Content-Type"] = "application/json"
        res = requests.post(base_url + url, headers=header)
        parse_data = json.loads(res.text)
        username = parse_data['data']['name']
        userdic = parse_data['data']['stId']
        print("当前用户名：" + username + "学号为" + str(userdic))
        return username
    except Exception as e:
        self.logger.error(e)
        return '失效了!'


def daka():
    accessDict = {}
    accessSend = {}
    accessLoc = {}
    accessNeed = {}
    # 获取姓名。
    for accessman in myget:
        # 获得的是个元组的集合，对这个集合进行处理
        # 由于0号是ID位，所以从1号开始,首先获取姓名
        print(accessman)
        accessDict[accessman[1]] = accessman[2]
        # 获取对应的邮箱
        accessSend[accessman[1]] = accessman[3]
        # 获取对应的data数据信息，注意要转换为对应格式
        accessLoc[accessman[1]] = eval(accessman[4])
        accessNeed[accessman[1]] = accessman[5]

    for accessToken in accessDict.keys():
        if accessNeed[accessToken] == 1:
            puncher = YiFuDao_Puncher(accessToken, accessDict[accessToken], accessLoc[accessToken])
            # 使用accessLoc的对应获取打卡位置
            locationdict = accessLoc[accessToken]["answerInfoList"][1]["location"]
            mylocation = locationdict["province"] + locationdict["city"] + locationdict["street"] + locationdict["area"] + \
                         locationdict["address"]
            title = "奕辅导健康打卡通知：{}".format(puncher.puncher_status)
            text = """
                    *** 奕辅导健康打卡通知 ***
                    时间：{}
                    打卡情况：{}，请检查打卡位置是否正确： 打卡位置:{},
                    """.format(datetime_2string(), puncher.puncher_status, mylocation)
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
            mail_receiver = []
            mail_receiver.append(accessSend[accessToken])
            ee = ErrorEmail(mail_sender, mail_auth_code, mail_receiver)
            msg = ee.theme_content(title, text)
            ee.send_message(mail_smtp_link, mail_smtp_port, msg)


# 主定时
myjob0 = schedule.every().day.at("18:05").do(daka)
# 备用定时
myjob = schedule.every().day.at("18:10").do(daka)
# 备用定时2
myjob2 = schedule.every().day.at("18:20").do(daka)
# 备用定时3
myjob2 = schedule.every().day.at("18:30").do(daka)

if __name__ == '__main__':
    daka()
    while True:
       print("等待打卡进度中……")
       schedule.run_pending()  # 运行所有可以运行的任务
       time.sleep(1)
