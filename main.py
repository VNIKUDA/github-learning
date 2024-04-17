# Імпорт модулів
from fastapi import FastAPI, HTTPException, Query, Request, File, UploadFile, Depends, Body
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Annotated
import os

from sqlalchemy.orm import Session
from db import models, schemas, crud
from db.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Отримати тільки ім'я з повного ім'я файлу
# def get_short_filename(filename):
#     filename = list(reversed(filename))
#     dot_index = filename.index(".")
#     file_type = "".join(reversed(filename[dot_index+1:]))

#     return file_type

def get_file_type(filename):
    filename = list(reversed(filename))
    dot_index = filename.index(".")
    file_type = "".join(reversed(filename[:dot_index+1]))

    return file_type


# Додаток 
app = FastAPI()
app.mount("/files", StaticFiles(directory="./files"), name="/files")

valid_files = (".mp3", ".m4a", ".ogg")

templates = Jinja2Templates("html_templates")


# CТВОРЕННЯ
# Створення автора
@app.post("/authors/create")
def create_author(author: schemas.AuthorCreate, db: Session = Depends(get_db)):
    return crud.create_author(db, author)

# Завантаження пісні та її створення
@app.post("/songs/create")
def create_and_upload_song(
    singer_id: Annotated[int, Query(...)], file: UploadFile, song: schemas.SongCreate = Depends(), db: Session = Depends(get_db)
):
    # Якщо такий пісня вже існує
    songs = crud.get_all_songs(db)
    songs_names = [song.name for song in songs]
    if song.name in songs_names:
        raise HTTPException(status_code=400, detail="Пісня з такою назвою вже існує")
    
    # Якщо не валідний тип файлу пісні
    if get_file_type(file.filename) not in valid_files:
        raise HTTPException(status_code=400, detail="Недопустимий тип файлу")
    
    # Запис файлу пісні на диск
    filename = f"{song.name}{get_file_type(file.filename)}"
    with open(f"files/{filename}", 'wb+') as file_:
        file_.write(file.file.read())

    return crud.create_song(db, song, filename, singer_id)

# Створення користувача
@app.post("/users/create")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

# Створення плейліста
@app.post("/playlists/create")
def create_playlist(user_id: Annotated[int, Query(...)], playlist: schemas.PlaylistCreate, db: Session = Depends(get_db)):
    return crud.create_playlist(db, playlist, user_id)


# ЗАПИТИ
# Відображення всіх доступних треків
@app.get('/songs/get-all', response_class=HTMLResponse)
def get_all_songs(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("get-all.html", {"request": request, "songs": crud.get_all_songs(db)})

# Прослухати трек
@app.get("/songs/listen", response_class=HTMLResponse)
def listen_song(song_id: Annotated[int, Query(...)], db: Session = Depends(get_db)):
    song = crud.get_song(db, song_id)
    html = f'<p style="font-size:6vh;"><b>{song.name}</b> song by {crud.get_author(db, song.singer_id).name}</p>'
    html += f'<audio controls src="/{song.filename}"></audio>'

    return html

# Послухати плейліст
@app.get("/playlists/listen", response_class=HTMLResponse)
def listen_playlist(playlist_id: int, db: Session = Depends(get_db)):
    playlist = crud.get_playlist(db, playlist_id)
    html = f'<h1>"<b>{playlist.title}</b>" playlist by <a href="#">{crud.get_user(db, playlist.user_id).nickname}</a></h1> <ul>'

    for song in playlist.songs:
        html += f'<li> <h3><b>{song.name}</b> song by <a href="#">{crud.get_author(db, song.singer_id).name}</a> <audio controls src="/{song.filename}">awdawd</audio> </li>'

    html += "</ul>"

    return html

@app.get("/authors/get")
def get_author_info(author_id: int, db: Session = Depends(get_db)):
    author = crud.get_author(db, author_id)
    return {
        "name": author.name,
        "songs": [song.name for song in author.songs]

    }



# ОНОВЛЕННЯ
# Додання пісні в плейліст
@app.put("/playlists/{playlist_id}/add-song")
def add_song_to_playlist(song_id: int, playlist_id: int, db: Session = Depends(get_db)):
    return crud.add_song_to_playlist(db, song_id, playlist_id)


# ВИДАЛЕННЯ
# Видалення пісні
@app.delete("/songs/delete")
def delete_song(song_id: Annotated[int, Query(...)], db: Session = Depends(get_db)):
    song_filename = crud.get_song(db, song_id).filename
    os.remove(f"./{song_filename}")
    return crud.delete_song(db, song_id)

# Видалення автора
@app.delete("/authors/delete")
def delete_author(author_id: Annotated[int, Query(...)], db: Session = Depends(get_db)):
    # Автор та його пісні
    author = crud.get_author(db, author_id)
    songs = author.songs

    # Видалення всіх пісень автора
    for song in songs:
        song_filename = crud.get_song(db, song.id).filename
        os.remove(f"./{song_filename}")
        crud.delete_song(db, song.id)


    
    # Видалення самого автора
    crud.delete_author(db, author_id)

    return author

# Видалення користувача
@app.delete("/users/delete")
def delete_user(user_id: Annotated[int, Query(...)], db: Session = Depends(get_db)):
    # Користувач та його плейлісти
    user = crud.get_user(db, user_id)
    playlists = user.playlists

    # Видалення всіх плейлистів користувача
    for playlist in playlists:
        for song in playlist.songs:
            crud.delete_song_from_playlist(db, song.id, playlist.id)

        crud.delete_playlist(db, playlist.id)

    # Видалення самого користувача
    crud.delete_user(db, user_id)

    return user

# Видалення плейліста
@app.delete("/playlists/delete")
def delete_playlist(playlist_id: int, db: Session = Depends(get_db)):
    playlist = crud.get_playlist(db, playlist_id)

    for song in playlist.songs:
        crud.delete_song_from_playlist(db, song.id, playlist_id)

    crud.delete_playlist(db, playlist_id)
    return playlist

# Видалення пісні з плейліста
@app.delete("/playlists/{playlist_id}/remove-song")
def remove_song_from_playlist(song_id: int, playlist_id: int, db: Session = Depends(get_db)):
    return crud.remove_song_from_playlist(db, song_id, playlist_id)