from flask import request, render_template, redirect, url_for, session, make_response
from flask_login import login_required, login_user, logout_user
from datetime import datetime
from datetime import timedelta

from app import app, bcrypt, login_manager, db_session
from sbs.models.tables import *
from sbs.utils import get_latest_account_num, get_account_balance, deposit_money_db, withdraw_money_db, \
    transfer_amount_db, get_transactions_from_db, get_otp, send_sms, get_bank_codes, get_latest_emp_id, \
    PrivilegeLevels, get_privilege_levels, get_privilege_value


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("bankPassword")
    user = OnlineUser.query.filter(OnlineUser.user_name == username).first()
    if user is not None:
        password_in_db = user.password
        if bcrypt.check_password_hash(password_in_db, password):
            session['privilege_level'] = user.privilege_level
            session['username'] = user.user_name
            session['account_number'] = user.account_number
            session['phone'] = user.phone
            otp = get_otp()
            send_sms(user.phone, otp)
            session['otp'] = otp
            return redirect(url_for('enter_otp'))
    return redirect(url_for('index'))


@app.route("/enter-otp")
def enter_otp():
    return render_template('input-otp.html', msg=request.args.get('msg'), function='verify_otp')


@app.route("/submit-otp", methods=['POST'])
def verify_otp():
    entered_otp = request.form.get('otp')
    if str(entered_otp).strip() == str(session['otp']).strip():
        user = OnlineUser.query.filter(OnlineUser.user_name == session['username']).first()
        login_user(user)
        if session['privilege_level'] == 0:
            return redirect(url_for('transactions'))
        else:
            return redirect(url_for('check_balance_with_account'))
    else:
        print('OTP verification failed!!')
        return redirect(url_for('enter_otp'))


@login_required
@app.route("/register")
def register():
    bcodes = [b[0] for b in get_bank_codes()]
    return render_template("sign-up.html", codes=bcodes)


@login_required
@app.route("/verify-user-details", methods=["POST"])
def verify_user_details():
    data = request.form
    account_number = get_latest_account_num(data.get('branch_code'))
    return render_template("verify-user-sign-up-details.html", data=data, account_number=account_number)


@login_required
@app.route("/register-user", methods=["POST"])
def register_user():
    print(request.form)
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    father_name = request.form.get('father_name')
    mother_name = request.form.get('mother_name')
    gender = request.form.get('gender')
    proof_id = request.form.get('proof_id')
    address_line1 = request.form.get('address_line1')
    address_line2 = request.form.get('address_line2')
    zip_code = request.form.get('zip_code')
    state = request.form.get('state')
    phone = request.form.get('phone')
    email_id = request.form.get('email_id')
    branch_code = request.form.get('branch_code')
    user_name = request.form.get('username')
    password = request.form.get('password')
    hashed_password = bcrypt.generate_password_hash(password)
    account_number = request.form.get('account_number')
    account_holder = AccountHolder(first_name=first_name,
                                   last_name=last_name,
                                   father_name=father_name,
                                   mother_name=mother_name,
                                   proof_id=proof_id,
                                   account_number=account_number,
                                   gender=gender,
                                   address_line1=address_line1,
                                   address_line2=address_line2,
                                   state=state,
                                   zip=zip_code,
                                   phone=phone,
                                   email_id=email_id,
                                   branch_code=branch_code)
    online_user = OnlineUser(user_name=user_name,
                             password=hashed_password,
                             account_number=account_number,
                             privilege_level=PrivilegeLevels.USER.value,
                             phone=phone)
    db_session.add(account_holder)
    db_session.add(online_user)
    db_session.commit()
    return redirect(url_for('check_balance_with_account'))


@login_required
@app.route("/register-employee")
def register_employee():
    if session["privilege_level"] < 7:
        return redirect(url_for("transactions"))
    emp_id = get_latest_emp_id()
    return render_template("create-employee.html", emp_id=emp_id, levels=get_privilege_levels())


@login_required
@app.route("/submit-emp-registration", methods=["POST"])
def add_emp_to_db():
    emp_name = request.form.get('employee_name')
    emp_id = request.form.get('emp_id')
    designation = request.form.get('designation')
    username = request.form.get('username')
    password = request.form.get('password')
    phone = request.form.get('phone')
    privilege_level = request.form.get('privilege_level')
    emp = Employee(emp_id=emp_id, emp_name=emp_name, designation=designation, phone=phone)
    online_user = OnlineUser(user_name=username, password=bcrypt.generate_password_hash(password),
                             employee_id=emp_id, privilege_level=get_privilege_value(privilege_level),
                             phone=phone)
    db_session.add(emp)
    db_session.commit()
    db_session.add(online_user)
    db_session.commit()
    print("Successfully registered")
    return redirect(url_for('check_balance_with_account'))


@login_required
@app.route("/transactions", methods=["GET"])
def transactions():
    if session['privilege_level'] == 0:
        all_transactions = get_transactions_from_db(session['account_number'])
        return render_template("transaction-details.html", transactions=all_transactions)
    elif session['privilege_level'] >= 5:
        return '<h1>In progress</h1>'


@login_required
@app.route("/check-balance-account-num")
def check_balance_with_account():
    if session['privilege_level'] < 5:
        return "<h1>Access Denied</h1>"
    return render_template("check-balance.html")


@login_required
@app.route("/get-account-balance")
def get_account_balance_route():
    if session['privilege_level'] < 5:
        return "<h1>Access Denied</h1>"
    account_number = request.args.get("account_number")
    back = request.args.get('back')
    if back is None:
        back = url_for('check_balance_with_account')
    balance = get_account_balance(account_number)
    return render_template("show-account-balance.html", account_number=account_number, balance=balance,
                           back=back)


@login_required
@app.route("/check-balance-self")
def get_account_balance_self():
    if session['privilege_level'] != 0:
        return "<h1>Access Denied<h1>"
    balance = get_account_balance(session['account_number'])
    return render_template("show-account-balance.html", account_number=session['account_number'], balance=balance,
                           back=url_for('transactions'))


@login_required
@app.route("/deposit-view")
def deposit_view():
    if session['privilege_level'] < 5:
        return "<h1>Access Denied<h1>"
    return render_template("deposit.html")


@login_required
@app.route("/withdraw-view")
def withdraw_view():
    if session['privilege_level'] < 5:
        return "<h1>Access Denied<h1>"
    return render_template("withdrawal.html")


@login_required
@app.route("/deposit-money", methods=["POST"])
def deposit():
    if session['privilege_level'] < 5:
        return "<h1>Access Denied<h1>"
    account_number = request.form.get("account_number")
    amount = float(request.form.get("amount"))
    ret = deposit_money_db(account_number, amount, "Amount deposited at bank")
    if ret[0]:
        return redirect(url_for('get_account_balance_route', account_number=account_number,
                                back=url_for('deposit_view')))
    else:
        return make_response('<h1>Internal error</h1>')


@login_required
@app.route("/withdraw-money", methods=["POST"])
def withdraw():
    if session['privilege_level'] < 5:
        return "<h1>Access Denied<h1>"
    account_number = request.form.get("account_number")
    amount = float(request.form.get("amount"))
    ret = withdraw_money_db(account_number, amount, "Amount withdrawn from bank")
    if ret[0]:
        return redirect(url_for('get_account_balance_route', account_number=account_number,
                                back=url_for('withdraw_view')))
    else:
        return make_response('<h1>Internal error</h1>')


@login_required
@app.route("/transfer-view")
def transfer_view():
    source_account_num = None
    if session['privilege_level'] == 0:
        source_account_num = session['account_number']
    return render_template("transfer-view.html", source_account_num=source_account_num)


def transfer_amount(source_account_num, rec_account_num, amount):
    ret = transfer_amount_db(source_account_num, rec_account_num, amount, "Amount transferred")
    if ret[0] and session['privilege_level'] >= 5:
        return redirect(url_for('get_account_balance_route', account_number=source_account_num,
                                back=url_for('transfer_view')))
    elif ret[0] and session['privilege_level'] == 0:
        return redirect(url_for('get_account_balance_self'))
    else:
        return '<h1>Error: {}</h1>'.format(ret[1])


@login_required
@app.route("/transfer-otp-view")
def transfer_otp_view():
    return render_template('input-otp.html', msg=request.args.get('msg'), function='transfer_otp_verify')


@login_required
@app.route("/transfer-otp-verify", methods=['POST'])
def transfer_otp_verify():
    entered_otp = request.form.get('otp')
    if str(entered_otp).strip() == str(session['transfer_otp']).strip():
        return transfer_amount(session['transfer_source'], session['transfer_rec'], session['transfer_amount'])
    else:
        print('OTP verification failed!!')
        return redirect(url_for('transfer_otp_view', msg='OTP Verification failed'))


@login_required
@app.route("/transfer", methods=["POST"])
def transfer():
    if session['privilege_level'] == 0 and request.form.get('src_account_number') != session['account_number']:
        print(session['account_number'], request.form.get('src_account_number'))
        return '<h1>Access Denied</h1>'
    source_account_num = request.form.get('src_account_number')
    rec_account_num = request.form.get('rec_account_number')
    amount = float(request.form.get('amount'))
    if amount > 1000:
        print('Amount greater than 10000')
        otp = get_otp()
        send_sms(session['phone'], otp)
        session['transfer_otp'] = otp
        session['transfer_otp_valid'] = datetime.now() + timedelta(minutes=5)
        session['transfer_source'] = source_account_num
        session['transfer_rec'] = rec_account_num
        session['transfer_amount'] = amount
        return redirect(url_for('transfer_otp_view'))
    return transfer_amount(source_account_num, rec_account_num, amount)



@login_required
@app.route("/logout")
def logout():
    print(logout_user())
    return redirect(url_for('index'))


@login_manager.user_loader
def load_user(_id):
    return db_session.query(OnlineUser).get(int(_id))
    # return OnlineUser.query.get(int(_id))


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
