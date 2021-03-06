import os
import subprocess
# import secrets
from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
# from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, SpellCheckerForm
from app.forms import RegistrationForm, LoginForm, SpellCheckerForm
# from app.models import User, SpellChecker
from app.models import User
from flask_login import login_user, current_user, logout_user, login_required

    

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title='Spell Checker Home')

@app.route("/register", methods=['GET','POST'])
def register():
    # if current_user.is_authenticated:
        # return redirect(url_for('home'))
    result_str = " "
    form = RegistrationForm()
    if request.method == 'GET':
        return render_template('register.html', title='Register', form=form, result_str=result_str)
    if form.validate_on_submit():
        # form.result.data = ""
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # user = User(username=form.username.data, phone=form.phone.data, email=form.email.data, password=hashed_password)
        user = User(username=form.username.data, phone=form.phone.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        # form.result.data = "success"
        result_str = "success"
        flash('success - Your account has been created - please log in!', 'success')
        # return redirect(url_for('login'))
    else:
        # form.result.data = "failure"
        result_str = "failure"        
        flash('failure - Acount Registration failed - please try again!', 'danger')
    return render_template('register.html', title='Register', form=form, result_str=result_str)
    
@app.route("/login", methods=['GET','POST'])
def login():
    # if current_user.is_authenticated:
        # return redirect(url_for('home'))
    result_str = " "
    form = LoginForm()
    if form.validate_on_submit():
        # form.result.data = ""
        user = User.query.filter_by(username=form.username.data).first()
        if not user or not bcrypt.check_password_hash(user.password, form.password.data):
            # form.result.data = "Incorrect Two-factor failure"
            result_str = "Incorrect Two-factor failure"
            flash('Two-factor failure - Login Unsuccessfull', 'danger')
        elif user.phone != form.phone.data:
            # form.result.data = "Incorrect Two-factor failure"
            result_str = "Incorrect Two-factor failure"
            flash('Two-factor failure - Login Unsuccessfull', 'danger')
        else:
            # form.result.data = "success."
            result_str = "success."
            login_user(user, remember=form.remember.data)
            # next_page = request.args.get('next')
            # return redirect(next_page) if next_page else redirect(url_for('spellcheck'))
    return render_template('login.html', title='Login', form=form, result_str=result_str)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


# def save_picture(form_picture):
    # random_hex = secrets.token_hex(8)
    # _, f_ext = os.path.splitext(form_picture.filename)
    # picture_fn = random_hex + f_ext
    # picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    # form_picture.save(picture_path)
    # return picture_fn
    
# @app.route("/account", methods=['GET','POST'])
# @login_required
# def account():
    # form = UpdateAccountForm()
    # if form.validate_on_submit():
        # if form.picture.data:
            # picture_file = save_picture(form.picture.data)
            # current_user.image_file = picture_file
        # current_user.username = form.username.data
        # current_user.email = form.email.data
        # current_user.phone = form.phone.data
        # db.session.commit()
        # flash('your account has been updated!', 'success')
        # return redirect(url_for('account'))
    # elif request.method == 'GET':
        # form.username.data = current_user.username
        # form.email.data = current_user.email
        # form.phone.data = current_user.phone
    # image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    # return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route("/spell_check", methods=['GET','POST'])
@login_required
def spellcheck():
    form = SpellCheckerForm()
    if form.validate_on_submit():
        input_text = form.input_content.data
        
        # spellcheck_file_path = os.path.join(app.root_path, 'a.out')
        spellcheck_file_path = './a.out'
        input_file_path = os.path.join(app.root_path, 'spell_check/input.txt')
        wordlist_file_path = os.path.join(app.root_path, 'spell_check/wordlist.txt')
        
        with open(input_file_path, 'w') as f:
            f.write(str(input_text))
        if not f:
            flash('Error creating input file for spell checker!', 'danger')
            return redirect(url_for('spellcheck'))

        form.input_content.data = input_text
        form.output_content.data = input_text        
#       misspelled_words = subprocess.run([spellcheck_file_path, input_file_path, wordlist_file_path], stdout=subprocess.PIPE).stdout.decode('utf-8')
        misspelled_words = subprocess.check_output([spellcheck_file_path, input_file_path, wordlist_file_path], stderr=subprocess.STDOUT).decode('utf-8')
        form.misspelled_content.data = misspelled_words.replace("\n", ", ").strip()[:-1]
    return render_template('spellcheck.html', form=form)
