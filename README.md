# 奕辅导健康打卡脚本

本项目为Python脚本所写，适合用于有python运行环境的机器。

其原项目来源于：https://github.com/zimin9/YiFuDaoPuncher


不熟悉python的小伙伴可以看一下基于云函数的打卡脚本，部署更加方便快捷：

https://github.com/Chorer/YiFuDaoChecker-cloudFunction

基于圈X，且功能更多的脚本：

https://github.com/uiolee/NanFuDao



### 📌 快速上手

#### 1、使用抓包软件获取自己奕辅导小程序账号的access_token



#### 2、部署到服务器，打开ip地址:5000/login

**2.1 登录打卡：**

账号密码是pinenut和pinenut111。
登录之后按照里面提示研究即可。每日6点05等时间打卡，如果需要改动，在主函数里修改这部分的时间。
```
# On startup, if this is main, this section of code will run
if __name__ == "__main__":
    # 主定时
    myjob0 = schedule.every().day.at("18:05").do(daka)
    # 备用定时
    myjob = schedule.every().day.at("18:10").do(daka)
    # 备用定时2
    myjob2 = schedule.every().day.at("18:20").do(daka)
```

**2.2 配置通知提醒**

我也忘了这边代码是咋回事了……反正我一直用的是邮箱打卡……应该和它下面的配置差不多。
```python
notify = "DingDing"
```

notify目前可以填入DingDing / Mail / PushPlus / None，分别对应钉钉机器人推送、邮件推送、PushPlus推送与无推送。

设置钉钉机器人时，需要把钉钉机器人的access_token与secret填入下方对应的变量：

```python
## 钉钉机器人配置:
# access_token
dingding_access_token = "9b121xxxxxxxxxxxxxx508be80a2097xxxxxxxxx"
# secret
dingding_secret = "SEC324xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx260243754ac07708ebb905"
```

设置邮箱提醒时，需要把发件人、授权码、收件人、smtp地址与端口填入下方对应的变量：

```python
## 邮箱配置：
# 发信人
mail_sender = "cxxxxxxxx@163.com"
# 授权码
mail_auth_code = "CxxxxxxxxxJO"
# 收件人
mail_receiver = ["3xxxxxxx99@qq.com"]
# smtp地址
mail_smtp_link = "smtp.163.com"
# smtp端口
mail_smtp_port = 465
```

以下是PushPlus推送的设置：

```python
# PushPlus配置：
# token
pushplus_token = "2exxxxxxxxxxxxxxxxxxxx0fcb0cbed3"
```



#### 3、配置python运行环境

```cmd
pip install -r requirements.txt
```


### 💬 反馈

全面放开了应该就没人反馈了吧……



### 📢 声明

1. 本项目仅供编程学习/个人使用，请遵守Apache-2.0 License开源项目授权协议。
2. 请在国家法律法规和校方相关原则下使用。
3. 开发者不对任何下载者和使用者的任何行为负责。



### 📆 相关计划

无
