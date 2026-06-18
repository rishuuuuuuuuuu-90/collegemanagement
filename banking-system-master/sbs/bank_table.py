from app import db


class Bank(db.Model):
    branch_name = db.Column(db.String(30), nullable=False, unique=True)
    branch_code = db.Column(db.String(30), nullable=False, primary_key=True)
    branch_address = db.Column(db.String(50), nullable=False)
