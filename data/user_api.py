from flask import (Flask, request, Blueprint, jsonify)

from data import db_session
from data.users import User

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
    elif request.json.get('id') in map(lambda u: u.id, db_sess.query(User).all()):
        return jsonify({'error': 'Id already exists'})
    
    bdate = datetime.datetime.date(datetime.datetime(year=int(request.json['bdate'].split('.')[0]),
                                                     month=int(request.json['bdate'].split('.')[1]),
                                                     day=int(request.json['bdate'].split('.')[2])))
    user = User(
        username=request.json['username'],
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
    if request.json.get('password') is not None:
        user.set_password(request.json['password'])
    
    db_sess.merge(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


if __name__ == '__main__':
    main()

