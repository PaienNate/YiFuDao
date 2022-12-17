from flask_login import UserMixin


class User(UserMixin):
    __username = "pinenut"
    __password = "pinenut111"
    __id = 1

    def __init__(self, username, password, id):
        self.username = username
        self.password = password
        self.id = id

    @classmethod
    def get(cls, id):
        return User(cls.__username, cls.__password, id)

    @classmethod
    def get_by_username(cls, username):
        if username == cls.__username:
            return User(cls.__username, cls.__password, cls.__id)
        else:
            return None

    def get_password(self):
        return self.password

    def verify_password(self, password):
        return self.password == password