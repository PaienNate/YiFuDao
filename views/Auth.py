from flask_wtf import Form, FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('用户:', [DataRequired()], render_kw={
        "class": "form-control", "placeholder": "请输入用户名(eg:zhangs)", "aria-describedby": "sizing-addon1"
    })
    password = PasswordField('密码:', [DataRequired()], render_kw={
        "class": "form-control", "placeholder": "请输入密码(eg:123456)", "aria-describedby": "sizing-addon1"
    })
    submit = SubmitField('登录')