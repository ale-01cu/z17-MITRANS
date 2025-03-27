from sqlalchemy import Column, Integer, String
from .db import Base

class Chat(Base):
    __tablename__ = "chats"

    # Identificador automático (autoincremental)
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Identificador manual que tú proporcionarás
    id_scraped = Column(String(50), unique=True, nullable=False)

    # URL de la imagen (puede ser opcional si quieres)
    last_text_url = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<Chat(id={self.id}, manual_id='{self.manual_id}', last_text_url='{self.last_text_url}')>"