from flask import Flask, render_template, redirect, url_for, request
from flask_login import (LoginManager, current_user, login_user, logout_user,
                         login_required)
from flask_restful import reqparse, abort, Api, Resource

from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired

from data import db_session
from data.users import User
from data.friend_request import FriendshipRequest
from data.messages import Message
from data.chats import Chat
from data.file import File
from data.login_form import LoginForm
from data.register_form import RegisterForm
from data.friendship_form import FriendshipForm
from data.edit_profile_form import EditProfileForm

import datetime
import os
import base64


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/', methods=['GET', 'POST'])
@app.route('/main', methods=['GET', 'POST'])
def main_page():
    if not current_user.is_authenticated:
        return redirect('/login')

    db_sess = db_session.create_session()
    current_user.last_online = datetime.datetime.now()
    db_sess.merge(current_user)
    db_sess.commit()

    friends = []
    ids = current_user.friends.split(', ')
    if '' in ids:
        ids.remove('')
    for friend_id in map(int, ids):
        friend = db_sess.query(User).filter(User.id == friend_id).first()
        if friend is not None:
            friends.append(friend)

    return render_template('main_page.html', title=f'Главная', friends=friends);


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль. Возможно, вы ещё не зарегистрированы.",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.bdate.data == None:
        form.bdate.data = datetime.datetime(datetime.datetime.now().year,
                                            datetime.datetime.now().month,
                                            datetime.datetime.now().day)

    if form.validate_on_submit():
        if form.password.data != form.password2.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким логином уже есть")

        if form.bdate.data == None:
            form.bdate.data = datetime.datetime(datetime.datetime.now().year,
                                                datetime.datetime.now().month,
                                                datetime.datetime.now().day)
        else:
            bdate = form.bdate.data

        user = User(
            username=form.username.data,
            bdate=bdate,
            descript=form.descript.data,
            city=form.city.data,
            last_online=datetime.datetime.now(),
            email=form.email.data,
            free_chat=form.free_chat.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        login_user(user, remember=True)
        return redirect("/")

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/profile/<int:id>', methods=['GET', 'POST'])
def profile(id):
    if current_user.is_authenticated:
        current_user.last_online = datetime.datetime.now()
    db_sess = db_session.create_session()
    current_user.last_online = datetime.datetime.now()
    db_sess.merge(current_user)
    db_sess.commit()
    user = db_sess.query(User).filter(User.id == id).first()
    if user is None:
        abort(404, message="Пользователя с таким id пока не существует")

    friends = []
    ids = user.friends.split(', ')
    if '' in ids:
        ids.remove('')
    for friend_id in map(int, ids):
        friend = db_sess.query(User).filter(User.id == friend_id).first()
        if friend is not None:
            friends.append(friend)

    request = db_sess.query(FriendshipRequest).filter(FriendshipRequest.from_id == current_user.id,
                                                      FriendshipRequest.to_id == id).first()

    print(user.id)
    return render_template('profile.html', title=f'Пользователь {id}', user=user, friends=friends, is_request=request is not None);


@app.route('/friendship_request/<int:id>', methods=['GET', 'POST'])
def friendship(id):
    if not current_user.is_authenticated:
        redirect('/login')
    db_sess = db_session.create_session()
    current_user.last_online = datetime.datetime.now()
    db_sess.merge(current_user)
    db_sess.commit()

    form = FriendshipForm()

    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.id == id).first()
        if user is None:
            return render_template('friendship_request.html', title='Запрос на дружбу',
                                   form=form,
                                   message="Пользователь с таким логином не найден")

        request = FriendshipRequest(
            text=form.text.data,
            from_id=current_user.id,
            to_id=id,
            sender_name=current_user.username,
            date=datetime.datetime.now()
        )
        
        db_sess.add(request)
        db_sess.commit()

        return redirect(f"/profile/{id}")

    return render_template('friendship_request.html', title='Запрос на дружбу', form=form)


@app.route('/my_requests', methods=['GET', 'POST'])
def my_requests():
    if not current_user.is_authenticated:
        redirect('/login')
    db_sess = db_session.create_session()
    current_user.last_online = datetime.datetime.now()
    db_sess.merge(current_user)
    db_sess.commit()

    requests = list(db_sess.query(FriendshipRequest).filter(FriendshipRequest.to_id == current_user.id))
    return render_template('my_requests.html', title='Запросы на вашу дружбу', requests=requests)


@app.route('/accept_request/<int:id>', methods=['GET', 'POST'])
def accept_request(id):
    if not current_user.is_authenticated:
        redirect('/login')
    db_sess = db_session.create_session()
    current_user.last_online = datetime.datetime.now()
    db_sess.merge(current_user)
    db_sess.commit()

    req = db_sess.query(FriendshipRequest).filter(FriendshipRequest.id == id).first()

    user_from = db_sess.query(User).filter(User.id == req.from_id).first()
    user_to = db_sess.query(User).filter(User.id == req.to_id).first()

    if req is None or user_from is None or user_to is None:
        abort(404)

    user_to.friends += ', ' + str(user_from.id)
    user_from.friends += ', ' + str(user_to.id)

    db_sess.merge(user_to)
    db_sess.merge(user_from)
    db_sess.delete(req)
    db_sess.commit()

    return redirect('/my_requests')


@app.route('/reject_request/<int:id>', methods=['GET', 'POST'])
def reject_request(id):
    if not current_user.is_authenticated:
        redirect('/login')
    db_sess = db_session.create_session()
    current_user.last_online = datetime.datetime.now()
    db_sess.merge(current_user)
    db_sess.commit()

    req = db_sess.query(FriendshipRequest).filter(FriendshipRequest.id == id).first()

    if req is None:
        abort(404)

    db_sess.delete(req)
    db_sess.commit()

    return redirect('/my_requests')


@app.route('/chat/<int:id>', methods=['GET', 'POST'])
def chat(id):
    if not current_user.is_authenticated:
        return redirect("/login")
    db_sess = db_session.create_session()
    current_user.last_online = datetime.datetime.now()
    db_sess.merge(current_user)
    db_sess.commit()

    if current_user.id == id:
        abort(404, message='Вы не можете писать сами себе')

    collab1 = f'{current_user.id}, {id}'
    collab2 = f'{id}, {current_user.id}'
    chat = db_sess.query(Chat).filter((Chat.collaborators == collab1) | (Chat.collaborators == collab2)).first()
    if chat is None:
        chat = Chat(
            collaborators=collab1
            )
        db_sess.add(chat)
        db_sess.commit()

    other = db_sess.query(User).filter(User.id == id).first()

    messages = db_sess.query(Message).filter(Message.chat_id == chat.id).all()
    images = {}
    files = {}

    if request.method == "POST":
        file = request.files.get('file')
        print(file)
        if request.form.get('message_button') and request.form.get('message_text') != '':
            msg = Message(
                chat_id = chat.id,
                sender_id = current_user.id,
                send_time = datetime.datetime.now())
            msg.coded_text = msg.code_text(request.form.get('message_text'))
            if file is not None:
                file_obj = File(
                    avaible_for = f'{current_user.id}, {other.id}',
                    name = file.filename,
                    content = file.read())
                db_sess.add(file_obj)
                db_sess.commit()
                file_id = file_obj.id
            msg.attached_file = file_id
            db_sess.add(msg)
            db_sess.commit()
            messages.append(msg)

    for msg in messages:
        if msg.attached_file is not None:
            file = db_sess.query(File).filter(File.id == msg.attached_file).first()
            if file is None:
                print('no such file')
                break
            print(file.name.split('.')[-1])
            if file.name.split('.')[-1] in ['png', 'jpg', 'bmp', 'gif', 'ico']:
                if not os.access(f'static/files/{file.name}', os.F_OK):
                    with open(f'static/files/{file.name}', 'wb') as f:
                        f.write(file.content)
                images[msg] = f'static/files/{file.name}'
            else:
                if not os.access(f'static/files/{file.name}', os.F_OK):
                    with open(f'static/files/{file.name}', 'wb') as f:
                        f.write(file.content)
                files[msg] = file.name

    return render_template('chat.html', title=other.username, messages=messages, other=other, message='', images=images, files=files, none=None)


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if not current_user.is_authenticated:
        redirect('/login')

    db_sess = db_session.create_session()
    current_user.last_online = datetime.datetime.now()
    db_sess.merge(current_user)
    db_sess.commit()

    form = EditProfileForm()
    if request.method == 'GET':
        form.username.data = current_user.username
        form.bdate.data = current_user.bdate
        form.descript.data = current_user.descript
        form.city.data = current_user.city
        form.email.data = current_user.email
        form.free_chat.data = current_user.free_chat

    if form.validate_on_submit():
        if form.bdate.data == None:
            form.bdate.data = datetime.datetime(datetime.datetime.now().year,
                                                datetime.datetime.now().month,
                                                datetime.datetime.now().day)
        else:
            bdate = form.bdate.data

        current_user.username = form.username.data
        current_user.bdate = bdate
        current_user.descript = form.descript.data
        current_user.city = form.city.data
        current_user.email = form.email.data
        current_user.free_chat = form.free_chat.data
        db_sess.merge(current_user)
        db_sess.commit()

        return redirect("/")

    return render_template('edit_profile.html', title=f'Редактировать профиль', form=form);


@app.route('/search', methods=['GET', 'POST'])
def search():
    if not current_user.is_authenticated:
        return redirect("/login")
    db_sess = db_session.create_session()
    current_user.last_online = datetime.datetime.now()
    db_sess.merge(current_user)
    db_sess.commit()

    users = []
    show_apologizion = False

    if request.method == "POST":
        if request.form.get('searchParam') == 'username':
            users = db_sess.query(User).filter(User.username.like(f"%{request.form.get('searchField')}%")).all()
        elif request.form.get('searchParam') == 'city':
            users = db_sess.query(User).filter(User.city.like(f"%{request.form.get('searchField')}%")).all()
        elif request.form.get('searchParam') == 'email':
            users = db_sess.query(User).filter(User.email.like(f"%{request.form.get('searchField')}%")).all()

        if len(users) > 20:
            users = users[:20]

        show_apologizion = True

    return render_template('search.html', title='Поиск', users=users, apolog=show_apologizion)


@app.route('/read_file/<filename>', methods=['GET'])
def read_file(filename):
    path = f'static/files/{filename}'
    if os.access(path, os.F_OK):
        with open(path, encoding='utf-8') as file:
            content = file.read()
            content.replace('\n', '<br />')
            return render_template('read_file.html', filename=filename, found=os.access(path, os.F_OK), content=content)
    return render_template('read_file.html', filename=filename, found=os.access(path, os.F_OK), content=content, message='Мы не нашли этот файл.')


def main():
    port = int(os.environ.get('PORT', 8080))
    
    db_session.global_init('db/users.db')
    app.run(host='0.0.0.0', port=port)


@login_manager.user_loader
def load_user(user_id):
    print(user_id)
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    main()
