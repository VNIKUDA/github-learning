from sqlalchemy.orm import Session
from . import models, schemas


# СТВОРЕННЯ
# Створення пісні
def create_song(db: Session, song: schemas.SongCreate, filename: str, singer_id: int):
    song = models.Song(name=song.name, filename=f"files/{filename}", singer_id=singer_id)

    db.add(song)
    db.commit()
    db.refresh(song)

    return song

# Створення автора
def create_author(db: Session, author: schemas.AuthorCreate):
    author = models.Author(name = author.name)

    db.add(author)
    db.commit()
    db.refresh(author)

    return author

# Створення користувача
def create_user(db: Session, user: schemas.UserCreate):
    user = models.User(nickname=user.nickname)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

# Створення плейліста
def create_playlist(db: Session, playlist: schemas.PlaylistCreate, user_id: int):
    playlist = models.Playlist(title=playlist.title, user_id=user_id)

    db.add(playlist)
    db.commit()
    db.refresh(playlist)

    return playlist

# ОТРИМАННЯ
# Отримати всі пісні
def get_all_songs(db: Session):
    return db.query(models.Song).all()

# Отримати пісню
def get_song(db: Session, song_id: int):
    return db.query(models.Song).filter(models.Song.id == song_id).first()

# Отримати автора
def get_author(db: Session, author_id: int):
    return db.query(models.Author).filter(models.Author.id == author_id).first()

# Отримати користувача
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

# Отримати плейліст
def get_playlist(db: Session, playlist_id: int):
    return db.query(models.Playlist).filter(models.Playlist.id == playlist_id).first()

# ОНОВЛЕННЯ
# Додати пісню в плейліст
def add_song_to_playlist(db: Session, song_id: int, playlist_id: int):
    new_relationship = {"song_id": song_id, "playlist_id": playlist_id}
    put_query = models.song_playlist_group.insert().values(**new_relationship)

    db.execute(put_query)
    db.commit()

    return new_relationship

# ВИДАЛЕННЯ
# Видалення пісні
def delete_song(db: Session, song_id: int):
    song = get_song(db, song_id)

    db.delete(song)
    db.commit()

    return song

# Видалення автора
def delete_author(db: Session, author_id: int):
    author = get_author(db, author_id)

    db.delete(author)
    db.commit()

    return author

# Видалення коричтувача
def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)

    db.delete(user)
    db.commit()

    return user

# Видалення плейліста
def delete_playlist(db: Session, playlist_id: int):
    playlist = get_playlist(db, playlist_id)

    db.delete(playlist)
    db.commit()

    return playlist

# Видалення пісні з плейліста
def remove_song_from_playlist(db: Session, song_id: int, playlist_id):

    delete_relation = models.song_playlist_group.delete().where(models.song_playlist_group.columns.song_id == song_id and models.song_playlist_group.columns.playlist_id == playlist_id)

    db.execute(delete_relation)
    db.commit()

    song = get_song(db, song_id)
    playlist = get_playlist(db, playlist_id)

    return f"{song.name} видалено з {playlist.title}"