from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from website import db

from .models import User

auth = Blueprint('auth', __name__)

# page (sign-up)
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    lang = session.get('lang', 'en')
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstname')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # check the formula
        if not email.endswith('@upm.edu.sa'):
            flash('Only @upm.edu.sa emails are allowed for registration', category='error') if lang == 'en' else flash(' فقط الإيميلات الجامعية @upm.edu.sa مسموحة للتسجيل', category='error')
            return redirect(url_for('auth.sign_up'))

        if password1 != password2:
            flash('Passwords do not match', category='error') if lang == 'en' else flash(' كلمة المرور غير متطابقة', category='error')
            return redirect(url_for('auth.sign_up'))

        if len(password1) < 7:
            flash('Password must be at least 7 characters long', category='error') if lang == 'en' else flash(' كلمة المرور يجب أن تكون 7 أحرف على الأقل', category='error')
            return redirect(url_for('auth.sign_up'))

        username_part = email.split('@')[0]

        # for Admins  (charecters)
        if username_part.isalpha():
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash(' Admin account already exists', category='error') if lang == 'en' else flash(' الحساب الإداري موجود مسبقًا', category='error')
            else:
                new_user = User(
                    email=email,
                    first_name=first_name,
                    password=generate_password_hash(password1, method='pbkdf2:sha256'),
                    user_type='admin'
                )
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                flash(' Admin account created successfully', category='success') if lang == 'en' else flash(' تم إنشاء حساب إداري بنجاح', category='success')
                return redirect(url_for('admin.dashboard'))

        # for students (numbers)
        elif username_part.isdigit():
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash(' Student already exists', category='error') if lang == 'en' else flash(' الطالب موجود مسبقًا', category='error')
            else:
                new_user = User(
                    email=email,
                    first_name=first_name,
                    password=generate_password_hash(password1, method='pbkdf2:sha256'),
                    user_type='student'
                )
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                flash(' Student account created successfully', category='success') if lang == 'en' else flash(' تم إنشاء حساب الطالب بنجاح', category='success')
                return redirect(url_for('views.home'))

        else:
            flash(' Invalid email format.', category='error') if lang == 'en' else flash(' صيغة البريد غير صالحة.', category='error')

    return render_template("sign_up.html", user=current_user, lang=lang)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    lang = session.get('lang', 'en')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password1')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            flash('Logged in successfully', category='success') if lang == 'en' else flash('تم تسجيل الدخول بنجاح', category='success')
            if user.user_type == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('views.home'))
        else:
            flash('Invalid email or password', category='error') if lang == 'en' else flash('الإيميل أو كلمة المرور غير صحيحة', category='error')

    return render_template("login.html", user=current_user, lang=lang)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))