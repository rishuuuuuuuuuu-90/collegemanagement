from app import db


class Employee(db.Model):
    emp_id = db.Column(db.String(10), primary_key=True)
    emp_name = db.Column(db.String(50))
    designation = db.Column(db.String(50))
