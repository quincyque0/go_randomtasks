import requests
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, status, Query, Path, Depends
import auth
from typing import List
from models import Book, BookCreate, User, BookUpdate # Добавьте User в импорты


tags_metadata = [{
    "name": "Books",
    "description": "Операция с книгами - получение всех, получение одной, создание, удаление, обновление книг"
}]


from typing import List, Optional


app = FastAPI(
    title="API Электронной библиотеки",
    description="Сервис для управления каталогом книг.",
    version="1.0.0",
    openapi_tags=tags_metadata
)
app.include_router(auth.router, tags=["auth"])
books = [
    Book(id=0, title="Ревизор", author="Гоголь", publication_year=1835),
    Book(id=1, title="Cкубиду", author="Шварцнегер", publication_year=2000),
    Book(id=2, title="Армяне и их повадки", author="Дикаприо", publication_year=2222)
]

next_book_id = 3



"""Переиндексирует книги после удаления"""
def reid():
    start = 0
    for i in books:
        i.id = start
        start +=1
        


@app.get("/books", response_model=List[Book],
    tags=["Books"],
    summary="Получить список всех книг",
    description="""
    Возвращает массив всех книг в библиотеке,
    фильтрация по автору с помощью query-параметра,
    получение полного списка книг.
    """)
def get_all_books(_author: Optional[str] = Query(None, description="Фильтр по автору",example="Гоголь")):

    """Получить все книги с возможностью фильтрации по автору"""
    if _author:
        filtered_books = [book for book in books if book.author.lower() == _author.lower()]
        return filtered_books
    else:
        return books
@app.get("/books/{book_id}", response_model=Book,
    tags=["Books"],
    summary="Получить одну книгу по id",
    description="""
    Возвращает объект книги, если она найдена,
    возвращает ошибку 404, если книга с таким id отсутствует,
    id должен быть неотрицательным числом
    """,
    responses={
        200: {"description": "Успешный ответ с данными книги"},
        404: {"description": "Книга не найдена"},
        400: {"description": "Неверный формат id"}
    })

def get_book(book_id: int = Path(..., description="ID книги для получения", example=1)):
    """
    Получает детальную информацию о книге по её уникальному id,
    возвращает объект книги, если она найдена,
    возвращает ошибку 404, если книга с таким id отсутствует.
    """
    try:
        return books[book_id]
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
@app.post("/books", 
    response_model=Book, 
    status_code=201,
    tags=["Books"],
    summary="Добавить новую книгу",
    description="""
    Создает новую запись о книге в библиотеке:
    
    Поля:
    ID присваивается автоматически
    title: Название книги
    author: Автор книги  
    publication_year: Год публикации
    """,
    responses={
        201: {"description": "Книга успешно создана"},
        400: {"description": "Неверные данные книги"}
    })
async def create_book(book: BookCreate,current_user: User = Depends(auth.get_current_user)):
    """Создать новую книгу"""
    _id = len(books)
    book = Book(
        id=_id,
        title=book.title,
        author=book.author,
        publication_year=book.publication_year
    )
    books.append(book)
    return book


@app.put("/books/{book_id}",
    response_model=Book,
    tags=["Books"],
    summary="Обновить информацию о книге",
    description="""
    Обновляет информацию о существующей книге,
    поля, не указанные в запросе, остаются без изменений.
    """,
    responses={
        200: {"description": "Книга успешно обновлена"},
        404: {"description": "Книга не найдена"}
    })
def update_book(book: BookUpdate, book_id: int = Path(..., description="id книги для обновления", example=1), current_user: User = Depends(auth.get_current_user)):
    """Обновить информацию о книге"""
    if(0 <= book_id and book_id < len(books)):
        current_book = books[book_id]
        update_data = book.dict(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None and value != "": 
                setattr(current_book, field, value)
    else : raise HTTPException(status_code=404, detail="Book not found")
    return current_book

@app.delete("/books/{book_id}",
    response_model=Book,
    tags=["Books"],
    summary="Удалить книгу",
    description="""
    Удаляет книгу из библиотеки по её id.
    
    После удаления происходит переиндексация всех книг.
    """,
    responses={
        200: {"description": "Книга успешно удалена"},
        404: {"description": "Книга не найдена"}
    })

def delete_book(book_id: int = Path(..., description="id удаляемой книги", example=1), current_user: User = Depends(auth.get_current_user)):
    """Удалить книгу"""
    if(0 <= book_id and book_id < len(books)):
        del(books[book_id])
        reid()
    else : raise HTTPException(status_code=404, detail="Book not found")
    