from flask import Flask, _app_ctx_stack
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from sbs.models.database import SessionLocal, engine, Base
from sqlalchemy.orm import scoped_session, Session

app = Flask(__name__)

# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost/banking_system"
db_session = scoped_session(SessionLocal, scopefunc=_app_ctx_stack.__ident_func__)
app.session = db_session
app.secret_key = "MySecureBankingApp"

login_manager = LoginManager(app)
bcrypt = Bcrypt(app)
Base.query = db_session.query_property()

from routes import *
from sbs.utils import PrivilegeLevels


def create_tables():
    Base.metadata.create_all(bind=engine)


def init():
    admin_user = 'MKK1'
    admin_password = bcrypt.generate_password_hash('admin')
    emp_id = 'E0001'
    emp_designation = 'DIRECTOR'
    emp_privilege_level = PrivilegeLevels.ADMINISTRATOR.value
    emp_name = 'M.K.K'
    phone = '+919717672711'
    branch_name = 'New India Branch'
    branch_code = 'NIB0001'
    branch_address = 'Plot number 20, Block-16, Delhi'
    emp_obj = Employee(emp_id=emp_id, emp_name=emp_name, designation=emp_designation, phone=phone)
    online_user = OnlineUser(user_name=admin_user, employee_id=emp_id, password=admin_password,
                             privilege_level=emp_privilege_level, phone=phone)
    bank = Bank(branch_name=branch_name, branch_code=branch_code, branch_address=branch_address)
    db_session.add(emp_obj)
    db_session.add(online_user)
    db_session.add(bank)
    db_session.commit()


if __name__ == '__main__':
    app.run('127.0.0.1', debug=True)
