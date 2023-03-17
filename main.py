from flask import Flask, render_template, redirect, url_for
from flask_login import (LoginManager, current_user, login_user, logout_user,
                         login_required)
from flask_restful import reqparse, abort, Api, Resource

from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired

from data import db_session
from data.users import User
from data.login_form import LoginForm
from data.register_form import RegisterForm

import datetime
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/', methods=['GET', 'POST'])
@app.route('/main', methods=['GET', 'POST'])
def main_page():
    '''if current_user.is_authenticated:
        db_sess = db_session.create_session()
        jobs = []
        team_leads = []
        collabs = []
        statuses = []
        images = []
        for job in db_sess.query(Jobs):
            print(job.job)
            if (str(current_user.id) in job.collaborators.split(', ') or
                current_user.id == job.team_leader):
                jobs.append(job)

                leader = db_sess.query(User).filter(User.id == job.team_leader).first()
                team_leads.append(f'{leader.name} {leader.surname}')
                collabs.append(', '.join([f'{u.name} {u.surname}' for u in db_sess.query(User)
                                          if (str(u.id) in job.collaborators.split(', ') or
                                              u.id == job.team_leader)]))
                
                if job.is_finished:
                    statuses.append('Работа успешно завершена')
                    images.append(url_for('static', filename='images/done.png'))
                elif datetime.datetime.now() < job.end_date:
                    statuses.append('Работа ещё выполняется')
                    images.append(url_for('static', filename='images/continues.png'))
                else:
                    statuses.append('Работа не выполнена, время вышло')
                    images.append(url_for('static', filename='images/time_out.png'))

        return render_template('main.html', title='Ваши работы', jobs=jobs,
                               team_leads=team_leads, collabs=collabs,
                               statuses=statuses, images=images,
                               indexes=list(range(len(jobs))))'''
    if current_user.is_authenticated:
        print(current_user.last_online)
    return redirect('/login')


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
                                   message="Такой пользователь уже есть")

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
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        login_user(user, remember=True)
        return redirect("/")

    return render_template('register.html', title='Регистрация', form=form)


'''@app.route('/add_job', methods=['GET', 'POST'])
def add_job():
    form = JobForm()
    form.start_date.data = datetime.datetime.now()
    if form.validate_on_submit():
        db_sess = db_session.create_session()

        if db_sess.query(User).filter(User.id == form.team_leader.data).first() is None:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message=f"Нет пользователя с индексом {form.team_leader.data}")
        for index in form.collaborators.data.split(', '):
            if db_sess.query(User).filter(User.id == int(index)).first() is None:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message=f"Нет пользователя с индексом {index}")

        
        if form.start_date.data == None:
            start = datetime.datetime.now()
        else:
            start = form.start_date.data
        end_date = start + datetime.timedelta(hours=form.work_size.data)
        print(end_date, start)
        job = Jobs(team_leader=form.team_leader.data,
                   job=form.job.data,
                   work_size=form.work_size.data,
                   collaborators=form.collaborators.data,
                   start_date=start, end_date=end_date,
                   is_finished=form.is_finished.data)
        db_sess.add(job)
        db_sess.commit()
        return redirect('/')
    return render_template('job.html', title='Новая работа', form=form)'''


def main():
    port = int(os.environ.get('PORT', 8080))
    
    db_session.global_init('db/users.db')
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
