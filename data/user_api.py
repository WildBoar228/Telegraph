from flask import (Flask, request, Blueprint, jsonify)

from data import db_session
from data.users import User
from data.chats import Chat
from data.messages import Message
from data.file import File

import datetime
import os


blueprint = Blueprint('all_users', __name__, template_folder='templates')


@blueprint.route('/api/user')
def get_all_users():
    db_sess = db_session.create_session()
    users = db_sess.query(Users).all()
    if not users:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'users': [item.to_dict(only=('username',
                                         'is_verified',
                                         'bdate',
                                         'descript',
                                         'friends',
                                         'city',
                                         'email',
                                         'last_online',
                                         'free_chat',
                                         'hashed_password'))
                      for item in users]
         }
    )


@blueprint.route('/api/user/<user_id>')
def get_one_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'error': 'Parameter must be a number'})
    if not user:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'user': job.to_dict(only=('username',
                                      'is_verified',
                                      'bdate',
                                      'descript',
                                      'friends',
                                      'city',
                                      'email',
                                      'last_online',
                                      'free_chat',
                                      'hashed_password'))
         }
    )


@blueprint.route('/api/user', methods=['POST'])
def create_user():
    db_sess = db_session.create_session()
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['username', 'bdate', 'descript', 'city',
                  'email', 'free_chat', 'password']):
        return jsonify({'error': 'Bad request'})
    elif db_sess.query(User).filter(User.email == request.json.get('email')).first():
        return jsonify({'error': 'User with this email already exists'})
    
    bdate = datetime.datetime.date(datetime.datetime(year=int(request.json['bdate'].split('.')[0]),
                                                     month=int(request.json['bdate'].split('.')[1]),
                                                     day=int(request.json['bdate'].split('.')[2])))
    user = User(
        username=request.json['username'],
        is_verified=False,
        bdate=bdate,
        descript=request.json['descript'],
        city=request.json['city'],
        email=request.json['email'],
        last_online=datetime.datetime.now(),
        free_chat=request.json['free_chat']
    )
    user.set_password(request.json['password'])
    db_sess.add(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/user/edit/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    db_sess = db_session.create_session()
    if not request.json:
        return jsonify({'error': 'Empty request'})

    user = db_sess.query(User).filter(User.id == user_id).first()
    if user is None:
        return jsonify({'error': 'No user with such id'})

    if request.json.get('password') is None:
        return jsonify({'error': 'You must enter this user\'s password'})
    if not user.check_password(request.json.get('password')):
        return jsonify({'error': 'Wrong password'})

    if request.json.get('username') is not None:
        user.username = request.json.get('username')
    if request.json.get('bdate') is not None:
        bdate = datetime.datetime.date(datetime.datetime(year=int(request.json['bdate'].split('.')[0]),
                                                         month=int(request.json['bdate'].split('.')[1]),
                                                         day=int(request.json['bdate'].split('.')[2])))
        user.bdate = bdate
    if request.json.get('descript') is not None:
        user.descript = request.json.get('descript')
    if request.json.get('city') is not None:
        user.city = request.json.get('city')
    if request.json.get('email') is not None:
        user.email = request.json.get('email')
    if request.json.get('free_chat') is not None:
        user.free_chat = request.json.get('free_chat')
    
    db_sess.merge(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/user/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    db_sess = db_session.create_session()
    if not request.json:
        return jsonify({'error': 'Empty request'})

    user = db_sess.query(User).filter(User.id == user_id).first()
    if user is None:
        return jsonify({'error': 'No user with such id'})

    if request.json.get('password') is None:
        return jsonify({'error': 'You must enter this user\'s password'})
    if not user.check_password(request.json.get('password')):
        admin = db_sess.query(User).filter(User.id == 1).first()
        print(request.json.get('password').split()[1])
        if admin is None or not admin.check_password(request.json.get('password').split()[1]):
            return jsonify({'error': 'Wrong password'})
    
    db_sess.delete(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/user/verify/<int:user_id>', methods=['POST'])
def verify_user(user_id):
    db_sess = db_session.create_session()
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['admin_password']):
        return jsonify({'error': 'Bad request'})

    admin = db_sess.query(User).get(1)

    if admin is None:
        return jsonify({'error': 'Admin doesn\'t exists yet. So who are you?'})
    
    if not admin.check_password(request.json.get('admin_password')):
        return jsonify({'error': 'It isn\'t admin\'s password. Good try :)'})

    user = db_sess.query(User).get(user_id)
    
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'error': 'Parameter must be a number'})
    if not user:
        return jsonify({'error': 'Not found'})

    user.is_verified = True
    db_sess.merge(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/user/deverify/<int:user_id>', methods=['POST'])
def deverify_user(user_id):
    db_sess = db_session.create_session()
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['admin_password']):
        return jsonify({'error': 'Bad request'})

    admin = db_sess.query(User).get(1)

    if admin is None:
        return jsonify({'error': 'Admin doesn\'t exists yet. So who are you?'})
    
    if not admin.check_password(request.json.get('admin_password')):
        return jsonify({'error': 'It isn\'t admin\'s password. Good try :)'})

    user = db_sess.query(User).get(user_id)
    
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'error': 'Parameter must be a number'})
    if not user:
        return jsonify({'error': 'Not found'})

    user.is_verified = False
    db_sess.merge(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/user/block/<int:user_id>', methods=['POST'])
def block_user(user_id):
    db_sess = db_session.create_session()
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['admin_password', 'reason']):
        return jsonify({'error': 'Bad request'})

    admin = db_sess.query(User).get(1)

    if admin is None:
        return jsonify({'error': 'Admin doesn\'t exists yet. So who are you?'})
    
    if not admin.check_password(request.json.get('admin_password')):
        return jsonify({'error': 'It isn\'t admin\'s password. Good try :)'})

    user = db_sess.query(User).get(user_id)
    
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'error': 'Parameter must be a number'})
    if not user:
        return jsonify({'error': 'Not found'})

    user.is_blocked = True
    user.block_reason = request.json.get('reason')
    db_sess.merge(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/user/unblock/<int:user_id>', methods=['POST'])
def unblock_user(user_id):
    db_sess = db_session.create_session()
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['admin_password']):
        return jsonify({'error': 'Bad request'})

    admin = db_sess.query(User).get(1)

    if admin is None:
        return jsonify({'error': 'Admin doesn\'t exists yet. So who are you?'})
    
    if not admin.check_password(request.json.get('admin_password')):
        return jsonify({'error': 'It isn\'t admin\'s password. Good try :)'})

    user = db_sess.query(User).get(user_id)
    
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'error': 'Parameter must be a number'})
    if not user:
        return jsonify({'error': 'Not found'})
    
    user.is_blocked = False
    user.block_reason = ''
    db_sess.merge(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/chat/send_message/<int:user_id>', methods=['POST'])
def send_message(user_id):
    db_sess = db_session.create_session()
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['id', 'password', 'text']):
        return jsonify({'error': 'Bad request'})

    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'error': 'Parameter must be a number'})
    user = db_sess.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})

    try:
        id_from = int(request.json["id"])
    except ValueError:
        return jsonify({'error': 'Parameter must be a number'})
    from_user = db_sess.query(User).get(id_from)
    if not from_user:
        return jsonify({'error': 'Not found'})
    if not from_user.check_password(request.json["password"]):
        return jsonify({'error': 'Wrong password'})
    if not user.free_chat and not str(id_from) in user.friends.split(', ') and id_from != 1:
        return jsonify({'error': 'You can\'t write messages to this user because you aren\'t his friend'})
    if request.json["text"] == '' and not request.json.get('file'):
        return jsonify({'error': 'Empty message'})
    if request.json.get('file') and not os.access(request.json.get('file'), os.F_OK):
        return jsonify({'error': 'File not found'})

    collab1 = f'{id_from}, {user_id}'
    collab2 = f'{user_id}, {id_from}'
    chat = db_sess.query(Chat).filter((Chat.collaborators == collab1) | (Chat.collaborators == collab2)).first()
    if chat is None:
        chat = Chat(
            collaborators=collab1
            )
        db_sess.add(chat)
        db_sess.commit()

    msg = Message(
        chat_id = chat.id,
        sender_id = id_from,
        send_time = datetime.datetime.now())
    msg.coded_text = msg.code_text(request.json.get('text'))

    if request.json.get('file'):
        with open(request.json.get('file'), 'rb') as file:
            file_obj = File(
                        avaible_for = collab1,
                        name = file.name.split('\\')[-1],
                        content = file.read())
        db_sess.add(file_obj)
        db_sess.commit()
        file_id = file_obj.id
        msg.attached_file = file_id

    db_sess.add(msg)
    db_sess.commit()

    return jsonify({'success': 'OK'})


if __name__ == '__main__':
    main()

