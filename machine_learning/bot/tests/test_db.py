from db.db import get_db, engine, Base
from sqlalchemy.orm.session import Session
import os


def test_local_db():
    """
    Verifica la correcta configuración de la base de datos local SQLite con SQLAlchemy.

    Esta función de prueba realiza dos comprobaciones principales:
    1. Que SQLAlchemy puede crear las tablas y establecer una sesión válida
    2. Que el archivo físico de la base de datos se ha creado en la ubicación esperada

    Proceso:
    - Crea todas las tablas definidas en los modelos usando Base.metadata.create_all()
    - Obtiene una sesión de base de datos mediante el generador get_db()
    - Verifica que el objeto de sesión sea una instancia válida de Session
    - Comprueba la existencia del archivo físico de la base de datos

    Excepciones:
    - Implicitamente captura AssertionError si alguna verificación falla

    Pre-condiciones:
    - Base (declarative_base) debe estar correctamente definido
    - El engine de SQLAlchemy debe estar configurado correctamente
    - La función get_db() debe estar disponible y ser un generador de sesiones

    Post-condiciones:
    - Las tablas se crean en la base de datos (si no existían)
    - La sesión queda abierta (debería cerrarse después)

    Ejemplo de uso:
    >>> test_local_db()
    (Ejecuta las verificaciones sin output si todo es correcto)

    Notas:
    - Esta prueba modifica el estado de la base de datos
    - El archivo se espera en '../instance/database.db' (relativo al working directory)
    """
    Base.metadata.create_all(bind=engine)

    db = next(get_db())
    assert isinstance(db, Session), \
        "La base de datos no se ha creado correctamente"

    db_file = "../instance/database.db"
    assert os.path.exists(db_file), \
        f"El archivo {db_file} no se ha creado"
