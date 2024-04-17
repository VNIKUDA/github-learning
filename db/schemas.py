from pydantic import BaseModel, Field
from typing import Annotated
from fastapi import UploadFile, File

# ПІСНЯ:
# База для пісні
class SongBase(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=30)]

# Створення пісні (тіло для запиту)
class SongCreate(SongBase):
    pass


class Song(SongBase):
    id: int
    filename: str
    singer_id: int
    playlists: list = []

    class Config:
        from_attributes = True
    

# АВТОР:
# База для автора
class AuthorBase(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=30)]

# Створення автора (тіло для запиту)
class AuthorCreate(AuthorBase):
    pass

# Автор (тіло для SQL)
class Author(AuthorBase):
    id: int
    songs: list = []

    class Config:
        from_attributes = True


# ПЛЕЙЛІСТ:
# База для плейліста
class PlaylistBase(BaseModel):
    title: Annotated[str, Field(min_length=3, max_length=30)]

# Свторення плейліста (тіло для запиту)
class PlaylistCreate(PlaylistBase):
    pass

# Плейліст
class Playlist(PlaylistBase):
    id: int
    user_id: int
    songs: list = []

    class Config:
        from_attributes = True


# КОРИСТУВАЧ:
# База для користувача
class UserBase(BaseModel):
    nickname: Annotated[str, Field(min_length=3, max_length=30)]

# Створеннч користувача (тіло для запиту)
class UserCreate(UserBase):
    pass

# Користувач
class User(UserBase):
    id: int
    playlists: list = []

    class Config:
        from_attributes = True