from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, name, _id):
        self.name = name
        self._id = _id

    def get_id(self):
        return self._id