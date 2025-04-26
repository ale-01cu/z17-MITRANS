from sqlalchemy import Column, Integer, String
from .db import Base

class Chat(Base):
    __tablename__ = "chats"

    # Identificador automático (autoincremental)
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Identificador manual que tú proporcionarás
    id_scraped = Column(String(50), unique=True, nullable=False)

    last_text = Column(String(500), nullable=True)

    msg2 = Column(String(500), nullable=True)
    msg3 = Column(String(500), nullable=True)
    msg4 = Column(String(500), nullable=True)
    msg5 = Column(String(500), nullable=True)

    last_text_index = Column(Integer, nullable=True)

    # URL de la imagen (puede ser opcional si quieres)
    last_text_url = Column(String(500), nullable=True)

    # Texto extraído del chat

    def __repr__(self):
        return (f"<Chat(id={self.id}, "
                f"id_scraped='{self.id_scraped}', "
                f"last_text_url='{self.last_text_url}')>")