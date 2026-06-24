# app/models.py
from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship  # Import natif indispensable ici

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    username: str = Field(unique=True, index=True, nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)
    password_hash: str = Field(nullable=False)
    role: str = Field(default="user")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # On passe directement l'objet relationship à sa_relationship
    audio_files: List[AudioFile] = Relationship(
        sa_relationship=relationship("AudioFile", back_populates="user", cascade="all, delete-orphan")
    )

class AudioFile(SQLModel, table=True):
    __tablename__ = "audio_files"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    
    user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    )
    
    file_name: str = Field(nullable=False)
    file_path: str = Field(nullable=False)
    format: str = Field(default="WAV")
    duration_seconds: float = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: User = Relationship(
        sa_relationship=relationship("User", back_populates="audio_files")
    )
    
    score: Optional[Score] = Relationship(
        sa_relationship=relationship("Score", back_populates="audio_file", uselist=False, cascade="all, delete-orphan")
    )

class Score(SQLModel, table=True):
    __tablename__ = "scores"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    
    audio_file_id: int = Field(
        sa_column=Column(Integer, ForeignKey("audio_files.id", ondelete="CASCADE"), unique=True, nullable=False)
    )
    
    tempo_bpm: int = Field(nullable=False)
    time_signature: str = Field(default="4/4")
    musical_data: str = Field(nullable=False)
    pdf_path: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    audio_file: AudioFile = Relationship(
        sa_relationship=relationship("AudioFile", back_populates="score")
    )