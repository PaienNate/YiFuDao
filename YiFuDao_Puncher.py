# -*- encoding:utf-8 -*-

import requests
import json
from utils.logger import logger
from default_data import punch_in_data as normal_data
from default_data import punch_in_data_2,punch_in_data_3

class YiFuDao_Puncher:
    def __init__(self, accessToken, username, loc):
        self.logger = logger('YiFuDaoPuncher.log')
        self.base_url = "https://yfd.ly-sky.com"
        self.header = {
            "accessToken": accessToken,
            "userAuthType": "MS"
        }
        self.punch_in_data = loc
        self.puncher_status = "π ζε‘θζ¬εε§εδΈ­"
        self.logger.info("π ζε‘θζ¬εε§εδΈ­")
        self.username = username
        self.check_in_index()

    def check_in_index(self):

        parse_data = ''
        try:
            url = "/ly-pd-mb/form/api/healthCheckIn/client/stu/index"
            res = requests.get(self.base_url + url, headers=self.header)
            parse_data = json.loads(res.text)
            detail = dict.get(parse_data, "data")
            id = dict.get(detail, "questionnairePublishEntityId")  # θ‘¨εIDοΌζ―ζ₯δΈε
            filling_status = dict.get(detail, "hadFill")  # ε‘«εηΆζ
            self.logger.info(self.username + "β ε·²θ·εε₯εΊ·ζε‘δΏ‘ζ―")
            self.logger.info(str(detail))
            self.puncher_status = self.username + "β ε·²θ·εε₯εΊ·ζε‘δΏ‘ζ―"
            if filling_status is False:
                self.logger.info(self.username + "β δ»ε€©ζζͺζε‘οΌε°θ―θΏθ‘ζε‘")
                self.puncher_status = self.username + "β δ»ε€©ζζͺζε‘οΌε°θ―θΏθ‘ζε‘"
                self.check_in_detail(str(id))
            else:
                self.logger.war(self.username + "β δ»ε€©ε·²η»ζε‘οΌθζ¬θͺε¨η»ζ")
                self.puncher_status = self.username + "β δ»ε€©ε·²η»ζε‘οΌθζ¬θͺε¨η»ζ"
                return 0
        except Exception as e:
            self.logger.error(self.username + "β θ·εε₯εΊ·ζε‘δΏ‘ζ―ε€±θ΄₯")
            self.logger.error(str(parse_data))
            self.logger.error(e)
            self.puncher_status = self.username + "β θ·εε₯εΊ·ζε‘δΏ‘ζ―ε€±θ΄₯"

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

            # ε€ζ­ι’θ?Ύη­ζ‘δΈε½ει?ε·ηι‘Ήζ―ε¦ηΈη¬¦
            if answer_id_list == question_id_list:
                self.punch_in_data["questionnairePublishEntityId"] = str(thisid)
                self.logger.info(self.username + "β ι’θ?Ύη­ζ‘δΈε½ει?ε·ηι‘ΉηΈη¬¦οΌζ¬ζ¬‘ζε‘ηι?ε·idδΈΊ{}".format(
                    self.punch_in_data["questionnairePublishEntityId"]))
                self.puncher_status = self.username + "β ι’θ?Ύη­ζ‘δΈε½ει?ε·ηι‘ΉηΈη¬¦οΌζ¬ζ¬‘ζε‘ηι?ε·idδΈΊ{}".format(
                    self.punch_in_data["questionnairePublishEntityId"])
                self.check_in_save()
            else:
                self.logger.error(self.username + "β ι’θ?Ύη­ζ‘δΈε½ει?ε·ηι‘ΉδΈηΈη¬¦,θζ¬ε·²η»ζ")
                self.puncher_status = self.username + "β ι’θ?Ύη­ζ‘δΈε½ει?ε·ηι‘ΉδΈηΈη¬¦,θζ¬ε·²η»ζοΌθ―·ζ£ζ₯οΌ"
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
                self.logger.info(self.username + "β ζε‘ζεοΌ{}".format(parse_data["message"]))
                self.puncher_status = self.username + "β ζε‘ζεοΌ{}".format(parse_data["message"])
            else:
                self.logger.error(self.username + "β ζε‘ε€±θ΄₯οΌ{}".format(parse_data["message"]))
                self.puncher_status = self.username + "β ζε‘ε€±θ΄₯οΌ{}".format(parse_data["message"])
                self.logger.error(parse_data)
        except Exception as e:
            self.logger.error(e)
