from sqlalchemy import  Table, Column, ForeignKey, String, Integer
from sqlalchemy.orm import relationship

from .database import Base

song_playlist_group = Table("song_playlist_group", Base.metadata, Column("song_id", Integer, ForeignKey("songs.id")), Column("playlist_id", Integer, ForeignKey("playlists.id")))


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)

    songs = relationship("Song", back_populates="singer")

class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    filename = Column(String, index=True)
    singer_id = Column(Integer, ForeignKey("authors.id"))

    singer = relationship("Author", back_populates="songs")
    playlists = relationship("Playlist", secondary=song_playlist_group, back_populates="songs")



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    nickname = Column(String, index=True)

    playlists = relationship("Playlist", back_populates="user")

class Playlist(Base):
    __tablename__= "playlists"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    # songs = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="playlists")
    songs = relationship("Song", secondary=song_playlist_group, back_populates="playlists")