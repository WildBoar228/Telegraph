from requests import post, get, delete
from datetime import datetime, timedelta

'''print(get('http://localhost:8080/api/user/12345').json()) # должно падать

print(post('http://localhost:8080/api/user', json={}).json()) # должно падать

print(post('http://localhost:8080/api/user',
           json={'username': 'Саня Санин',
                 'bdate': '2006.03.03',
                 'descript': 'Просто чел',
                 'friends': '',
                 'city': 'Душанбе',
                 'email': 'ujshifd@yandex.ru',
                 'last_online': datetime.isoformat(datetime.now()),
                 'free_chat': False}).json()) # должно падать'''

print(post('http://localhost:8080/api/user',
           json={'username': 'Саня Санин',
                 'bdate': '2006.12.20',
                 'descript': 'Просто чел',
                 'city': 'Новый Уренгой',
                 'email': 'ujshifd@yandex.ru',
                 'free_chat': True,
                 'password': '228228'}).json()) # не должно падать

'''print(post('http://localhost:8080/api/user/edit/312441',
           json={'bdate': '2006.12.20',
                 'city': 'Новый Уренгой'}).json()) # должно падать

print(post('http://localhost:8080/api/user/edit/2',
           json={'bdate': '2006.12.20',
                 'city': 'Новый Уренгой'}).json()) # должно падать

print(post('http://localhost:8080/api/user/edit/2',
           json={'bdate': '2006.12.20',
                 'city': 'Новый Уренгой',
                 'password': '228'}).json()) # должно падать

print(post('http://localhost:8080/api/user/edit/2',
           json={'bdate': '2006.12.20',
                 'city': 'Новый Уренгой',
                 'password': '228228'}).json()) # не должно падать'''

'''print(delete('http://localhost:8080/api/user/delete/2',
             json={'password': 'admin JH&#j3hGrtd@^&62gfhj#'}).json()) # не должно падать'''

'''print(post('http://localhost:8080/api/user/verify/2',
           json={'admin_password': 'JH&#j3hGrtd@^&62gfhj#'}).json())'''

print(post('http://localhost:8080/api/user',
           json={'username': 'Игорь Головаченко',
                 'bdate': '2007.09.30',
                 'descript': 'Создатель',
                 'city': 'Минск',
                 'email': 'igolovachenko@yandex.ru',
                 'free_chat': True,
                 'password': '228228'}).json())

'''print(post('http://localhost:8080/api/chat/send_message/2',
           json={'id': 3,
                 'password': '228228'}).json())

print(post('http://localhost:8080/api/chat/send_message/2',
           json={'id': 3,
                 'password': '228228',
                 'text': 'Здарова кабан'}).json())

print(post('http://localhost:8080/api/chat/send_message/2',
           json={'id': 3,
                 'password': '228228',
                 'text': 'Здарова кабан',
                 'file': 'C:\\Users\\Игорь\\Desktop\\Питон\\Pillow\\p.png'}).json())'''

'''print(post('http://localhost:8080/api/chat/send_message/4',
           json={'id': 1,
                 'password': 'JH&#j3hGrtd@^&62gfhj#',
                 'text': 'Дамы и господа, женщины и люди, добро пожаловать в мой мессенджер!'
                 }).json())'''

print(post('http://localhost:8080/api/user/unblock/2',
           json={'admin_password': 'JH&#j3hGrtd@^&62gfhj#'}).json())
