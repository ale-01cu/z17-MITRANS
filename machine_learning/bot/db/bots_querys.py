from sqlalchemy.orm import Session
from .db import get_db
from .models import Bot
from typing import Optional, List


class BotQuerys:
    def __init__(self, db: Session = next(get_db())):
        self.db = db

    def create_bot(self, name: str, is_in_message_requests_view: bool = False) -> Bot:
        """
        Crea un nuevo bot en la base de datos
        :param name: Nombre único del bot
        :param is_in_message_requests_view: Estado de visibilidad en solicitudes de mensaje
        :return: Objeto Bot creado
        """
        db_bot = Bot(name=name, is_in_message_requests_view=is_in_message_requests_view)
        self.db.add(db_bot)
        self.db.commit()
        self.db.refresh(db_bot)
        return db_bot

    def get_bot(self, bot_id: int) -> Optional[Bot]:
        """
        Obtiene un bot por su ID
        :param bot_id: ID del bot a buscar
        :return: Objeto Bot o None si no existe
        """
        return self.db.query(Bot).filter(Bot.id == bot_id).first()

    def get_bot_by_name(self, name: str) -> Optional[Bot]:
        """
        Obtiene un bot por su nombre
        :param name: Nombre del bot a buscar
        :return: Objeto Bot o None si no existe
        """
        return self.db.query(Bot).filter(Bot.name == name).first()

    def get_all_bots(self, skip: int = 0, limit: int = 100) -> List[Bot]:
        """
        Obtiene todos los bots con paginación
        :param skip: Número de bots a saltar (para paginación)
        :param limit: Número máximo de bots a devolver
        :return: Lista de objetos Bot
        """
        return self.db.query(Bot).offset(skip).limit(limit).all()

    def update_bot(
            self,
            name: Optional[str] = None,
            is_in_message_requests_view: Optional[bool] = None
    ) -> Optional[Bot]:
        """
        Actualiza un bot existente
        :param name: Nuevo nombre del bot (opcional)
        :param is_in_message_requests_view: Nuevo estado de visibilidad (opcional)
        :return: Objeto Bot actualizado o None si no existe
        """
        db_bot = self.get_bot_by_name(name=name)
        if db_bot:
            if name is not None:
                db_bot.name = name
            if is_in_message_requests_view is not None:
                db_bot.is_in_message_requests_view = is_in_message_requests_view

            self.db.commit()
            self.db.refresh(db_bot)
        return db_bot

    def delete_bot(self, bot_id: int) -> bool:
        """
        Elimina un bot de la base de datos
        :param bot_id: ID del bot a eliminar
        :return: True si se eliminó, False si no existía
        """
        db_bot = self.get_bot(bot_id)
        if db_bot:
            self.db.delete(db_bot)
            self.db.commit()
            return True
        return False

    def bot_exists(self, name: str) -> bool:
        """
        Verifica si un bot con el nombre dado ya existe
        :param name: Nombre del bot a verificar
        :return: True si existe, False si no
        """
        return self.db.query(Bot).filter(Bot.name == name).first() is not None