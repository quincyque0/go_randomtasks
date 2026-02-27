import requests
import json

BASE_URL = "http://127.0.0.1:8000"
AUTH_TOKEN = None



def get_all():
    print("Получение списка ресурсов")
    try:
        
        key = input("выполнить поиск по автору? (1)")
        if(key == '1'):
            author = input("автор: ")
            response = requests.get('http://127.0.0.1:8000/books',params={'_author' : author})
        else : response = requests.get('http://127.0.0.1:8000/books')
        response.raise_for_status()
        if response.status_code == 200:
            print("Status code 200 OK")
        else:
            print(f"Status code {response.status_code}")

        data = response.json()
            
        

        for i in data:
            print(i)
        print("\n")

    except requests.exceptions.RequestException as a:
        print(a)


def get_one():
    print("Получение одного ресурса")
    try:
        bookId = int(input("введите номер книги\n"))
        response1 = requests.get(f'http://127.0.0.1:8000/books/{bookId}')

        response1.raise_for_status()
        if response1.status_code == 200:
            print("Status code 200 OK")
        else:
            print(f"Status code {response1.status_code}")
        data1 = response1.json()


        for key, value in data1.items():
            print(f"{key}: {value}\n")
        print("\n")
    except requests.exceptions.RequestException as a:
        print(a)


def create_book():
    if not AUTH_TOKEN:
        print("Вы не зарегестрированы") 
    print("Создание нового ресурса")
    try:
        title1 = input("title: ")
        publication_year1 = int(input("year of publication"))
        author1 = input("author")

        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        dic = dict(title = title1, author =  author1,publication_year = publication_year1)
        response2 = requests.post("http://127.0.0.1:8000/books",json=dic,headers=headers)

        response2.raise_for_status()
        if response2.status_code == 201:
            print("Status code 201 Created")
        else:
            print(f"Status code {response2.status_code}")
            print("\n")
    except requests.exceptions.RequestException as a:
        print(a)


def update_book():

    
    if not AUTH_TOKEN:
        print("Вы не зарегестрированы")
    print("Обновление ресурса")
    
    try:
        id1 = int(input("book id: "))
        dic = {}
        title1 = input("title (Enter чтобы пропустить): ").strip()
        if title1:
            dic["title"] = title1
        author1 = input("author (Enter чтобы пропустить): ").strip()
        if author1:
            dic["author"] = author1
        year_input = input("year of publication (Enter чтобы пропустить): ").strip()
        if year_input:
            try:
                dic["publication_year"] = int(year_input)
            except ValueError:
                print("год должен быть числом")
                return
            
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response3 = requests.put(f"http://127.0.0.1:8000/books/{id1}", json=dic,headers=headers)
        response3.raise_for_status()
        if response3.status_code == 200:
            print("Status code 200 Updated")
            print("Книга успешно обновлена!")
        else:
            print(f"Status code {response3.status_code}")
        
        print("\n")
        
    except requests.exceptions.HTTPError as e:
        print(e)


def delete_book():
    if not AUTH_TOKEN:
        print("Вы не зарегестрированы")
    print("Удаление книженции")
    try:
        id1 = input("book id")
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response4 = requests.delete(f"http://127.0.0.1:8000/books/{id1}",headers=headers)
        if response4.status_code == 200:
            print("Status code 200 Deleted")
        else:
            print(f"Status code {response4.status_code}")
            print("\n")
    except requests.exceptions.RequestException as a:
        print(a)


def register_user():
    username = input("Enter username: ")
    password = input("Enter password: ")
    response = requests.post(f"{BASE_URL}/register", json={"username": username, "password": password})
    if response.status_code == 200:
        print("Registration successful!")
        print(response.json())
    else:
        print(f"Error: {response.status_code} - {response.text}")




def login_user():
    global AUTH_TOKEN
    username = input("Enter username: ")
    password = input("Enter password: ")
    response = requests.post(f"{BASE_URL}/token", data={"username": username, "password": password})
    if response.status_code == 200:
        AUTH_TOKEN = response.json().get("access_token")
        print("Login successful. Token stored.")
    else:
        print(f"Error: {response.status_code} - {response.text}")


def control():
    while(1):
        print("1 - искать во всех\n2 - вывести книгу по id\n3 - создать книгу\n4 - обновить информацию о книге по id\n5 - удалить кингу по id \n6 - зарегестрироваться \n7 -  логин")
        move = input("выбирете действие : ")
        match(move):
            case '1':
                get_all()
            case '2':
                bookId = int(input(" id книги : "))
                get_one(bookId)
            case '3':
                create_book()
            case '4':
                update_book()
            case '5':
                delete_book()
            case '6':
                register_user()
            case '7':
                login_user()
            case _:
                break
control()

