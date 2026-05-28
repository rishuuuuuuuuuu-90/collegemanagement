from app import db


class AccountHolder(db.Model):
    account_number = db.Column(db.String(30), nullable=False, primary_key=True)
    gender = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(13), nullable=False)
    address = db.Column(db.String(50))
    email_id = db.Column(db.String(50))
    branch_code = db.Column(db.String(30), db.ForeignKey("bank.branch_code"), nullable=False)

