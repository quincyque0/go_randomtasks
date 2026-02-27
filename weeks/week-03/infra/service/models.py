from typing import Optional
from pydantic import BaseModel, Field

class Book(BaseModel):
    id: int = Field(description="Уникальный идентификатор книги", example=1)
    title: str = Field(description="Название книги", example="Преступление и наказание")
    author: str = Field(description="Автор книги", example="Фёдор Достоевский")
    publication_year: int = Field(description="Год публикации", example=1866)

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Название книги", example="Обновленное название")
    author: Optional[str] = Field(None, description="Автор книги", example="Обновленный автор")
    publication_year: Optional[int] = Field(None, description="Год публикации", example=2024)
    
class BookCreate(BaseModel):
    title: str = Field(description="Название книги", example="Новая книга")
    author: str = Field(description="Автор книги", example="Новый автор")
    publication_year: int = Field(description="Год публикации", example=2024)


class User(BaseModel):
    username: str


class UserCreate(User):
    password: str


class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None