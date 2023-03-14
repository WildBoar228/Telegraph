from requests import post, get, delete
from flask import jsonify

print(get('http://localhost:8080/api/v2/users/12345'))

print(delete('http://localhost:8080/api/v2/users/12345'))

print(post('http://localhost:8080/api/v2/users'))

print(post('http://localhost:8080/api/v2/users',
           json={'name': 'Саня',
                 'surname': 'Санин',
                 'age': 99,
                 'position': '-',
                 'speciality': 'archer',
                 'address': 'Moscow, Kremlin',
                 'email': 'sanya@sanya.ru'}).json())

print(post('http://localhost:8080/api/v2/users',
           json={'name': 'Саня',
                 'surname': 'Санин',
                 'age': 99,
                 'position': '-',
                 'speciality': 'archer',
                 'address': 'Moscow, Kremlin',
                 'email': 'sanya@sanya.ru',
                 'password': '1234567890'}).json())

print(delete('http://localhost:8080/api/v2/users/1'))
