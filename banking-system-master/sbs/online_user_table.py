from app import db
from flask_login import UserMixin


class OnlineUser(db.Model, UserMixin):
    _id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(30), nullable=False, unique=True)
    account_number = db.Column(db.String(30), db.ForeignKey('account_holder.account_number'), unique=True)
    employee_id = db.Column(db.String(30), db.ForeignKey('employee.emp_id'), unique=True)
    password = db.Column(db.String(60), nullable=False)
    privilege_level = db.Column(db.Integer, nullable=False, default=0) # 10 is the highest privilege level

    def get_id(self):
        return self._id
