from sqlalchemy.orm import Session
from .db import get_db
from .models import Chat
from typing import Optional, List


class ChatQuerys:
    def __init__(self, db: Session = next(get_db())):
        self.db = db


    def create_chat(self, id_scraped: str, last_text_url: Optional[str] = None) -> Chat:
        """
        Crea un nuevo chat en la base de datos
        :param id_scraped: Identificador manual del chat
        :param last_text_url: URL de la imagen (opcional)
        :return: Objeto Chat creado
        """
        db_chat = Chat(id_scraped=id_scraped, last_text_url=last_text_url)
        self.db.add(db_chat)
        self.db.commit()
        self.db.refresh(db_chat)
        return db_chat


    def get_chat(self, chat_id: int) -> Optional[Chat]:
        """
        Obtiene un chat por su ID
        :param chat_id: ID del chat a buscar
        :return: Objeto Chat o None si no existe
        """
        return self.db.query(Chat).filter(Chat.id == chat_id).first()


    def get_chat_by_id_scraped(self, id_scraped: str) -> Optional[Chat]:
        """
        Obtiene un chat por su identificador manual
        :param id_scraped: Identificador manual del chat
        :return: Objeto Chat o None si no existe
        """
        return self.db.query(Chat).filter(Chat.id_scraped == id_scraped).first()


    def get_all_chats(self, skip: int = 0, limit: int = 100) -> List[Chat]:
        """
        Obtiene todos los chats con paginación
        :param skip: Número de chats a saltar (para paginación)
        :param limit: Número máximo de chats a devolver
        :return: Lista de objetos Chat
        """
        return self.db.query(Chat).offset(skip).limit(limit).all()


    def update_chat(self, chat_id: int, id_scraped: Optional[str] = None,
                    last_text_url: Optional[str] = None) -> Optional[Chat]:
        """
        Actualiza un chat existente
        :param chat_id: ID del chat a actualizar
        :param id_scraped: Nuevo identificador manual (opcional)
        :param last_text_url: Nueva URL de imagen (opcional)
        :return: Objeto Chat actualizado o None si no existe
        """
        db_chat = self.get_chat(chat_id)
        if db_chat:
            if id_scraped is not None:
                db_chat.id_scraped = id_scraped
            if last_text_url is not None:
                db_chat.last_text_url = last_text_url
            self.db.commit()
            self.db.refresh(db_chat)
        return db_chat


    def delete_chat(self, chat_id: int) -> bool:
        """
        Elimina un chat de la base de datos
        :param chat_id: ID del chat a eliminar
        :return: True si se eliminó, False si no existía
        """
        db_chat = self.get_chat(chat_id)
        if db_chat:
            self.db.delete(db_chat)
            self.db.commit()
            return True
        return False