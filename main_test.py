# -*- encoding:utf-8 -*-
import json
import time

import requests

from YiFuDao_Puncher import YiFuDao_Puncher
from default_data import *
from utils.dingding_bot import DingDingBot
from utils.pushplus import PushPlus
from utils.smtp_sender import ErrorEmail
from utils.time_util import datetime_2string
import schedule


def get_user_name(accessToken):
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
    file = open("sample.txt", encoding='utf-8')
    for line in file:
        # 用井号区分开自己的备注名和对方的名称,第三个是它的QQ号，第四个判断，默认1是原本的，2/3是专属的
        linelist = line.replace('\n', '').split('#')
        accessDict[linelist[0]] = linelist[1]
        accessSend[linelist[0]] = linelist[2]
        accessLoc[linelist[0]] = linelist[3]
    file.close()
    # 获取姓名。
    for accessToken in accessDict.keys():
        get_user_name(accessToken)
        puncher = YiFuDao_Puncher(accessToken, accessDict[accessToken], accessLoc[accessToken])
        title = "奕辅导健康打卡通知：{}".format(puncher.puncher_status)
        text = """
                *** 奕辅导健康打卡通知 ***
                时间：{}
                打卡情况：{}
                """.format(datetime_2string(), puncher.puncher_status)

        if notify == "DingDing":
            notifier = DingDingBot(dingding_access_token, dingding_secret)
            notifier.set_msg(title, text)
            notifier.send()
        elif notify == "Mail":
            # 默认钉钉会有提示
            notifier = DingDingBot(dingding_access_token, dingding_secret)
            notifier.set_msg(title, text)
            notifier.send()
            # 然后给每个人发消息
            mail_receiver = []
            mail_receiver.append(accessSend[accessToken])
            ee = ErrorEmail(mail_sender, mail_auth_code, mail_receiver)
            msg = ee.theme_content(title, text)
            ee.send_message(mail_smtp_link, mail_smtp_port, msg)
        elif notify == "PushPlus":
            notifier = PushPlus.send(pushplus_token, title, text, "markdown")
        del puncher
# 主定时
myjob0 = schedule.every().day.at("18:12").do(daka)
# 备用定时
myjob = schedule.every().day.at("18:20").do(daka)
# 备用定时2
myjob2 = schedule.every().day.at("18:40").do(daka)

if __name__ == '__main__':
    daka()
