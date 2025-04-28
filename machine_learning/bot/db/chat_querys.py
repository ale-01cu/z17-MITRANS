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


    def update_chat_by_chat_id(self, chat_id: int,
                    last_text_url: Optional[str] = None, last_text: Optional[str] = None,
                    last_text_index: int = 0) -> Optional[Chat]:
        """
        Actualiza un chat existente
        :param chat_id: ID del chat a actualizar
        :param id_scraped: Nuevo identificador manual (opcional)
        :param last_text_url: Nueva URL de imagen (opcional)
        :param last_text_index: Índice del texto en la lista de textos (opcional)
        :return: Objeto Chat actualizado o None si no existe
        """
        db_chat = self.get_chat(chat_id)
        if db_chat:
            if last_text_url is not None:
                db_chat.last_text_url = last_text_url
            if last_text is not None:
                db_chat.last_text = last_text

            db_chat.last_text_index = last_text_index
            self.db.commit()
            self.db.refresh(db_chat)
        return db_chat


    def update_chat_by_chat_id_scraped(self, id_scraped: str,
                    last_text_url: Optional[str] = None, last_text: Optional[str] = None,
                    msg2: Optional[str] = None, msg3: Optional[str] = None, msg4: Optional[str] = None,
                    msg5: Optional[str] = None, last_text_index: int = 0) -> Optional[Chat]:

        """
        Actualiza un chat existente
        :param id_scraped: Nuevo identificador manual (opcional)
        :param last_text_url: Nueva URL de imagen (opcional)
        :param last_text_index: Índice del texto en la lista de textos (opcional)
        :return: Objeto Chat actualizado o None si no existe
        """
        db_chat = self.get_chat_by_id_scraped(id_scraped)
        if db_chat:
            if last_text_url is not None:
                db_chat.last_text_url = last_text_url
            if last_text is not None:
                db_chat.last_text = last_text
            if msg2 is not None:
                db_chat.msg2 = msg2
            if msg3 is not None:
                db_chat.msg3 = msg3
            if msg4 is not None:
                db_chat.msg4 = msg4
            if msg5 is not None:
                db_chat.msg5 = msg5

            db_chat.last_text_index = last_text_index
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