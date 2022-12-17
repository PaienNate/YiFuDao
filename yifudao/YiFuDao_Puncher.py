# -*- encoding:utf-8 -*-

import requests
import json
from utils.logger import logger

class YiFuDao_Puncher:
    def __init__(self, accessToken, username, loc):
        self.logger = logger('YiFuDaoPuncher.log')
        self.base_url = "https://yfd.ly-sky.com"
        self.header = {
            "accessToken": accessToken,
            "userAuthType": "MS"
        }
        self.punch_in_data = loc
        self.puncher_status = "💚 打卡脚本初始化中"
        self.logger.info("💚 打卡脚本初始化中")
        self.username = username
        self.check_in_index()

    def check_in_index(self):

        parse_data = ''
        try:
            url = "/ly-pd-mb/form/api/healthCheckIn/client/stu/index"
            res = requests.get(self.base_url + url, headers=self.header)
            parse_data = json.loads(res.text)
            detail = dict.get(parse_data, "data")
            id = dict.get(detail, "questionnairePublishEntityId")  # 表单ID，每日不同
            filling_status = dict.get(detail, "hadFill")  # 填写状态
            self.logger.info(self.username + "✔ 已获取健康打卡信息")
            self.logger.info(str(detail))
            self.puncher_status = self.username + "✔ 已获取健康打卡信息"
            if filling_status is False:
                self.logger.info(self.username + "✔ 今天暂未打卡，尝试进行打卡")
                self.puncher_status = self.username + "✔ 今天暂未打卡，尝试进行打卡"
                self.check_in_detail(str(id))
            else:
                self.logger.war(self.username + "❗ 今天已经打卡，脚本自动结束")
                self.puncher_status = self.username + "❗ 今天已经打卡，脚本自动结束"
                return 0
        except Exception as e:
            self.logger.error(self.username + "❌ 获取健康打卡信息失败")
            self.logger.error(str(parse_data))
            self.logger.error(e)
            self.puncher_status = self.username + "❌ 获取健康打卡信息失败"

    def check_in_detail(self, thisid):
        try:
            url = "/ly-pd-mb/form/api/questionnairePublish/" + str(thisid) + "/getDetailWithAnswer"
            res = requests.get(self.base_url + url, headers=self.header)
            parse_data = json.loads(res.text)
            subjectList = dict.get(dict.get(dict.get(parse_data, "data"), "questionnaireWithSubjectVo"), "subjectList")

            question_id_list = []
            answer_id_list = []
            for i in subjectList:
                question_id_list.append(i["id"])
            for i in self.punch_in_data["answerInfoList"]:
                answer_id_list.append(i["subjectId"])

            # 判断预设答案与当前问卷的项是否相符
            if answer_id_list == question_id_list:
                self.punch_in_data["questionnairePublishEntityId"] = str(thisid)
                self.logger.info(self.username + "✔ 预设答案与当前问卷的项相符，本次打卡的问卷id为{}".format(
                    self.punch_in_data["questionnairePublishEntityId"]))
                self.puncher_status = self.username + "✔ 预设答案与当前问卷的项相符，本次打卡的问卷id为{}".format(
                    self.punch_in_data["questionnairePublishEntityId"])
                self.check_in_save()
            else:
                self.logger.error(self.username + "❌ 预设答案与当前问卷的项不相符,脚本已结束")
                self.puncher_status = self.username + "❌ 预设答案与当前问卷的项不相符,脚本已结束，请检查！"
                return 0
        except Exception as e:
            self.logger.error(e)

    def check_in_save(self):
        try:
            url = "/ly-pd-mb/form/api/answerSheet/saveNormal"
            header = self.header
            header["Content-Type"] = "application/json"
            res = requests.post(self.base_url + url, data=json.dumps(self.punch_in_data), headers=header)
            parse_data = json.loads(res.text)
            print(parse_data)
            if parse_data["code"] == 200:
                self.logger.info(self.username + "✔ 打卡成功，{}".format(parse_data["message"]))
                self.puncher_status = self.username + "✔ 打卡成功，{}".format(parse_data["message"])
            else:
                self.logger.error(self.username + "❌ 打卡失败，{}".format(parse_data["message"]))
                self.puncher_status = self.username + "❌ 打卡失败，{}".format(parse_data["message"])
                self.logger.error(parse_data)
        except Exception as e:
            self.logger.error(e)
