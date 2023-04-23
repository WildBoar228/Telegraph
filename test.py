from requests import post, get
from datetime import datetime, timedelta

print(get('http://localhost:8080/api/user/12345').json()) # должно падать

print(post('http://localhost:8080/api/user', json={}).json()) # должно падать

print(post('http://localhost:8080/api/user',
           json={'username': 'Саня Санин',
                 'bdate': '2006.03.03',
                 'descript': 'Просто чел',
                 'friends': '',
                 'city': 'Душанбе',
                 'email': 'ujshifd@yandex.ru',
                 'last_online': datetime.isoformat(datetime.now()),
                 'free_chat': False}).json()) # должно падать

print(post('http://localhost:8080/api/user',
           json={'username': 'Саня Санин',
                 'bdate': '2006.03.03',
                 'descript': 'Просто чел',
                 'city': 'Душанбе',
                 'email': 'ujshifd@yandex.ru',
                 'free_chat': False,
                 'password': '228228'}).json()) # не должно падать

print(post('http://localhost:8080/api/user/edit/312441',
           json={'bdate': '2006.12.20',
                 'city': 'Новый Уренгой'}).json()) # должно падать

print(post('http://localhost:8080/api/user/edit/3',
           json={'bdate': '2006.12.20',
                 'city': 'Новый Уренгой'}).json()) # должно падать

print(post('http://localhost:8080/api/user/edit/3',
           json={'bdate': '2006.12.20',
                 'city': 'Новый Уренгой',
                 'password': '228'}).json()) # должно падать

print(post('http://localhost:8080/api/user/edit/3',
           json={'bdate': '2006.12.20',
                 'city': 'Новый Уренгой',
                 'password': '228228'}).json()) # не должно падать

