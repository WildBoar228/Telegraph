from flask import Flask, render_template, redirect, url_for, request, abort
from flask_login import (LoginManager, current_user, login_user, logout_user,
                         login_required)

from data import db_session, user_api
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
import platform

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

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

    agent = request.headers.get('User-Agent')
    is_mobile = ('iphone' or 'android' or 'blackberry') in agent.lower()
            
    return render_template('main_page.html', is_mobile=is_mobile, title=f'Главная', friends=friends);


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        current_user.last_online = datetime.datetime.now()
        db_sess.merge(current_user)
        db_sess.commit()

    agent = request.headers.get('User-Agent')
    is_mobile = ('iphone' or 'android' or 'blackberry') in agent.lower()

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

    return render_template('login.html', is_mobile=is_mobile, title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        current_user.last_online = datetime.datetime.now()
        db_sess.merge(current_user)
        db_sess.commit()

    agent = request.headers.get('User-Agent')
    is_mobile = ('iphone' or 'android' or 'blackberry') in agent.lower()

    form = RegisterForm()
    if form.bdate.data == None:
        form.bdate.data = datetime.datetime(datetime.datetime.now().year,
                                            datetime.datetime.now().month,
                                            datetime.datetime.now().day)

    if form.validate_on_submit():
        if form.password.data != form.password2.data:
            return render_template('register.html', is_mobile=is_mobile, title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', is_mobile=is_mobile, title='Регистрация',
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
    
    return render_template('register.html', is_mobile=is_mobile, title='Регистрация', form=form)


@app.route('/profile/<int:id>', methods=['GET', 'POST'])
def profile(id):
    if not current_user.is_authenticated:
        return redirect('/login')

    agent = request.headers.get('User-Agent')
    is_mobile = ('iphone' or 'android' or 'blackberry') in agent.lower()
    
    db_sess = db_session.create_session()
    current_user.last_online = datetime.datetime.now()
    db_sess.merge(current_user)
    db_sess.commit()
    
    user = db_sess.query(User).filter(User.id == id).first()
    if user is None:
        return "Пользователя с таким id пока не существует"

    if request.method == 'POST':
        req = db_sess.query(FriendshipRequest).filter(FriendshipRequest.to_id == current_user.id,
                                                       FriendshipRequest.from_id == id).first()
        if request.form.get('accept-request') is not None:
            current_user.friends += ', ' + str(id)
            user.friends += ', ' + str(current_user.id)

            db_sess.merge(current_user)
            db_sess.merge(user)
            db_sess.delete(req)
            db_sess.commit()

        if request.form.get('reject-request') is not None:
            db_sess.delete(req)
            db_sess.commit()

    friends = []
    ids = user.friends.split(', ')
    if '' in ids:
        ids.remove('')
    for friend_id in map(int, ids):
        friend = db_sess.query(User).filter(User.id == friend_id).first()
        if friend is not None:
            friends.append(friend)

    our_request = db_sess.query(FriendshipRequest).filter(FriendshipRequest.from_id == current_user.id,
                                                          FriendshipRequest.to_id == id).first()
    his_request = db_sess.query(FriendshipRequest).filter(FriendshipRequest.to_id == current_user.id,
                                                          FriendshipRequest.from_id == id).first()
    
    return render_template('profile.html', is_mobile=is_mobile, title=f'Пользователь {id}', user=user, friends=friends, is_our_request=our_request is not None, is_his_request=his_request is not None, request=his_request);


@app.route('/friendship_request/<int:id>', methods=['GET', 'POST'])
def friendship(id):
    if not current_user.is_authenticated:
        redirect('/login')

    try:
        agent = request.headers.get('User-Agent')
        is_mobile = ('iphone' or 'android' or 'blackberry') in agent.lower()
    except UnboundLocalError:
        is_mobile=True

    db_sess = db_session.create_session()
    current_user.last_online = datetime.datetime.now()
    db_sess.merge(current_user)
    db_sess.commit()

    form = FriendshipForm()

    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.id == id).first()
        if user is None:
            return render_template('friendship_request.html', is_mobile=is_mobile, title='Запрос на дружбу',
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
    
    return render_template('friendship_request.html', is_mobile=is_mobile, title='Запрос на дружбу', form=form)


@app.route('/my_requests', methods=['GET', 'POST'])
def my_requests():
    if not current_user.is_authenticated:
        redirect('/login')
    db_sess = db_session.create_session()
    current_user.last_online = datetime.datetime.now()
    db_sess.merge(current_user)
    db_sess.commit()

    agent = request.headers.get('User-Agent')
    is_mobile = ('iphone' or 'android' or 'blackberry') in agent.lower()

    requests = list(db_sess.query(FriendshipRequest).filter(FriendshipRequest.to_id == current_user.id))
    return render_template('my_requests.html', is_mobile=is_mobile, title='Запросы на вашу дружбу', requests=requests)


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

    agent = request.headers.get('User-Agent')
    is_mobile = ('iphone' or 'android' or 'blackberry') in agent.lower()

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
        filename = request.files.get('file').filename
        if request.form.get('message_button') and (request.form.get('message_text') != '' or filename != ''):
            msg = Message(
                chat_id = chat.id,
                sender_id = current_user.id,
                send_time = datetime.datetime.now())
            msg.coded_text = msg.code_text(request.form.get('message_text'))
            if filename != '':
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
                break
            if file.name.split('.')[-1] in ['png', 'jpg', 'bmp', 'gif', 'ico']:
                if not os.access(f'static/files/{file.name}', os.F_OK):
                    with open(f'static/files/{file.name}', 'wb') as f:
                        f.write(file.content)
                images[msg] = (file, file.path == '', f'static/files/{file.name}')
            else:
                files[msg] = (file, file.path == '')

        if msg.sender_id != current_user.id and not msg.is_read:
            msg.is_read = True
            db_sess.merge(msg)
            db_sess.commit()

    return render_template('chat.html', is_mobile=is_mobile, title=other.username, messages=messages, other=other, message='', images=images, files=files, none=None)


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if not current_user.is_authenticated:
        redirect('/login')

    agent = request.headers.get('User-Agent')
    is_mobile = ('iphone' or 'android' or 'blackberry') in agent.lower()

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
    
    return render_template('edit_profile.html', is_mobile=is_mobile, title=f'Редактировать профиль', form=form);


@app.route('/search', methods=['GET', 'POST'])
def search():
    if not current_user.is_authenticated:
        return redirect("/login")
    db_sess = db_session.create_session()
    current_user.last_online = datetime.datetime.now()
    db_sess.merge(current_user)
    db_sess.commit()

    agent = request.headers.get('User-Agent')
    is_mobile = ('iphone' or 'android' or 'blackberry') in agent.lower()

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
    
    return render_template('search.html', is_mobile=is_mobile, title='Поиск', users=users, apolog=show_apologizion)


@app.route('/load_file/<int:file_id>', methods=['GET', 'POST'])
def load_file(file_id):
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        current_user.last_online = datetime.datetime.now()
        db_sess.merge(current_user)
        db_sess.commit()

    agent = request.headers.get('User-Agent')
    is_mobile = ('iphone' or 'android' or 'blackberry') in agent.lower()

    file = db_sess.query(File).filter(File.id == file_id).first()
    
    if request.method == "POST":
        directory = request.form.get('dir')
        if request.form.get('save_button') is not None:
            if os.path.isdir(directory):
                with open(directory + '/' + file.name, 'wb') as f:
                    f.write(file.content)
            else:
                return render_template('load_file.html', is_mobile=is_mobile, file=file, message='This path doesn\'t exist')
            file.path = directory
            db_sess.merge(file)
            db_sess.commit()
            return render_template('load_file.html', is_mobile=is_mobile, file=file, message='File was saved successfully')
    
    return render_template('load_file.html', is_mobile=is_mobile, file=file)


@app.route('/my_chats', methods=['GET'])
def my_chats():
    if not current_user.is_authenticated:
        return redirect("/login")
    db_sess = db_session.create_session()
    current_user.last_online = datetime.datetime.now()
    db_sess.merge(current_user)
    db_sess.commit()

    agent = request.headers.get('User-Agent')
    is_mobile = ('iphone' or 'android' or 'blackberry') in agent.lower()

    chats = []
    others = {}
    last_sender = {}
    last_msg = {}
    last_files = {}
    unread_msgs = {}
    for chat in db_sess.query(Chat).all():
        if str(current_user.id) in chat.collaborators.split(', '):
            chats.append(chat)
            other = chat.collaborators.split(', ')
            other.remove(str(current_user.id))
            others[chat] = db_sess.query(User).filter(User.id == int(other[0])).first()

            messages = db_sess.query(Message).filter(Message.chat_id == chat.id).all()
            unread_count = len(db_sess.query(Message).filter(Message.chat_id == chat.id).filter(Message.is_read == 0).filter(Message.sender_id != current_user.id).all())
            unread_msgs[chat] = unread_count
            if len(messages) > 0:
                last = max(messages, key=lambda m: m.send_time)
                last_sender[chat] = db_sess.query(User).filter(User.id == last.sender_id).first()
                text = last.decode_text(last.coded_text)
                if len(text) > 50:
                    text = text[:47].rstrip('.') + '...'
                if last.attached_file is not None:
                    att_file = db_sess.query(File).filter(File.id == last.attached_file).first()
                    filename = att_file.name
                    if len(text) > 50 - len(filename) - 5:
                        text = text[:(50 - len(filename) - 5)].rstrip('.') + '... ';
                    last_files[chat] = filename
                last_msg[chat] = text
            else:
                last_sender[chat] = ''
                last_msg[chat] = ''
                
    return render_template('my_chats.html', is_mobile=is_mobile, chats=chats, others=others, last_sender=last_sender, last_msg=last_msg, last_files=last_files, unread_msgs=unread_msgs)


def main():
    port = int(os.environ.get('PORT', 8080))
    
    db_session.global_init('db/users.db')
    app.register_blueprint(user_api.blueprint)
    app.run(host='0.0.0.0', port=port)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    main()
