from flask_login import UserMixin
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Float

from .database import Base


class AccountHolder(Base):
    __tablename__ = 'account_holder'
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30), nullable=False)
    father_name = Column(String(50), nullable=False)
    mother_name = Column(String(50), nullable=False)
    proof_id = Column(String(50), nullable=False)
    account_number = Column(String(30), nullable=False, primary_key=True)
    gender = Column(String(10), nullable=False)
    address_line1 = Column(String(50))
    address_line2 = Column(String(50))
    state = Column(String(50))
    zip = Column(String(10))
    phone = Column(String(13), nullable=False)
    email_id = Column(String(50))
    branch_code = Column(String(30), ForeignKey("bank.branch_code"), nullable=False)


class Bank(Base):
    __tablename__ = 'bank'
    branch_name = Column(String(30), nullable=False, unique=True)
    branch_code = Column(String(30), nullable=False, primary_key=True)
    branch_address = Column(String(50), nullable=False)


class Employee(Base):
    __tablename__ = 'employee'
    emp_id = Column(String(10), primary_key=True)
    emp_name = Column(String(50))
    designation = Column(String(50))
    phone = Column(String(13), nullable=False)


class OnlineUser(Base, UserMixin):
    __tablename__ = 'online_user'
    _id = Column(Integer, primary_key=True)
    user_name = Column(String(30), nullable=False, unique=True)
    account_number = Column(String(30), ForeignKey('account_holder.account_number'), unique=True)
    employee_id = Column(String(30), ForeignKey('employee.emp_id'), unique=True)
    password = Column(String(60), nullable=False)
    privilege_level = Column(Integer, nullable=False, default=0)
    phone = Column(String(13), nullable=False)

    def get_id(self):
        return self._id


class Transaction(Base):
    __tablename__ = 'transaction'
    transaction_id = Column(String(30), primary_key=True)
    transaction_time = Column(DateTime, nullable=False)
    account_number = Column(String(30), ForeignKey("account_holder.account_number"), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(10), nullable=False)
    details = Column(String(100))

    @staticmethod
    def get_credit_type():
        return "CREDIT"

    @staticmethod
    def get_debit_type():
        return "DEBIT"
