from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel

#==========================================
# 1. TABLE USERS
#==========================================
class User(SQLModel, table=True):
    tablename = "users"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    username: str = Field(unique=True, index=True, nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)
    password_hash: str = Field(nullable=False)
    role: str = Field(default="user")  # 'admin' ou 'user'
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relations SQLModel (pour faciliter les requêtes Python)
    audio_files: List["AudioFile"] = Relationship(
        back_populates="user", 
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


#==========================================
# 2. TABLE AUDIO_FILES
#==========================================
class AudioFile(SQLModel, table=True):
    tablename = "audio_files"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE")
    file_name: str = Field(nullable=False)
    file_path: str = Field(nullable=False)
    format: str = Field(default="WAV")
    duration_seconds: float = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relations
    user: User = Relationship(back_populates="audio_files")
    score: Optional["Score"] = Relationship(
        back_populates="audio_file", 
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"}
    )
#==========================================
# 3. TABLE SCORES (Partitions)
#==========================================
class Score(SQLModel, table=True):
    tablename = "scores"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    audio_file_id: int = Field(foreign_key="audio_files.id", ondelete="CASCADE", unique=True)
    tempo_bpm: int = Field(nullable=False)
    time_signature: str = Field(default="4/4")
    musical_data: str = Field(nullable=False)  # Tu pourras y stocker ton JSON_DATA sous forme de texte
    pdf_path: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relation
    audio_file: AudioFile = Relationship(back_populates="score")