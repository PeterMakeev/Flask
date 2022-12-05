import requests

HOST = 'http://127.0.0.1:5000'


def post():
    post_data = {
        'title': 'Garage sale',
        'description': 'Garage for sale in excellent condition',
        'owner': 'Alex'
    }
    response = requests.post(f'{HOST}/market', json=post_data)
    print(response.status_code)
    print(response.text)


def get(id: int):
    response = requests.get(f'{HOST}/market/{id}')
    print(response.text)


def delete(id: int):
    response = requests.delete(f'{HOST}/market/{id}')
    print(response.text)


#Создаём объявление
post()

#Получаем нужное объявление
get(1)

#Удаляем нужное объявление
#delete(1)