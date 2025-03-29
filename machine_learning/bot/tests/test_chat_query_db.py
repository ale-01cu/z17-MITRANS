from db.models import Chat
from db.chat_querys import ChatQuerys# Asegúrate de importar correctamente tus clases
from db.db import get_db

def test_create_chat():
    db = next(get_db())
    querys = ChatQuerys(db=db)

    # Crear un nuevo chat
    new_chat = querys.create_chat(id_scraped="test_id", last_text_url="http://example.com/image.jpg")

    # Verificar que el chat se creó correctamente
    assert new_chat.id is not None
    assert new_chat.id_scraped == "test_id"
    assert new_chat.last_text_url == "http://example.com/image.jpg"

    # Verificar que el chat existe en la base de datos
    db_chat = db.query(Chat).filter(Chat.id_scraped == "test_id").first()
    assert db_chat is not None
    assert db_chat.id == new_chat.id


def test_get_chat():
    db = next(get_db())
    querys = ChatQuerys(db=db)

    # Crear un chat para buscarlo
    new_chat = querys.create_chat(id_scraped="test_id_2")

    # Obtener el chat por su ID
    retrieved_chat = querys.get_chat(chat_id=new_chat.id)

    # Verificar que el chat recuperado es correcto
    assert retrieved_chat is not None
    assert retrieved_chat.id == new_chat.id
    assert retrieved_chat.id_scraped == "test_id_2"

    # Intentar obtener un chat inexistente
    non_existent_chat = querys.get_chat(chat_id=9999)
    assert non_existent_chat is None


def test_get_chat_by_id_scraped():
    db = next(get_db())
    querys = ChatQuerys(db=db)

    # Crear un chat para buscarlo
    new_chat = querys.create_chat(id_scraped="unique_id")

    # Obtener el chat por su id_scraped
    retrieved_chat = querys.get_chat_by_id_scraped(id_scraped="unique_id")

    # Verificar que el chat recuperado es correcto
    assert retrieved_chat is not None
    assert retrieved_chat.id_scraped == "unique_id"
    assert retrieved_chat.id == new_chat.id

    # Intentar obtener un chat inexistente
    non_existent_chat = querys.get_chat_by_id_scraped(id_scraped="nonexistent")
    assert non_existent_chat is None


def test_get_all_chats():
    db = next(get_db())
    querys = ChatQuerys(db=db)

    # Crear varios chats
    querys.create_chat(id_scraped="chat1")
    querys.create_chat(id_scraped="chat2")
    querys.create_chat(id_scraped="chat3")

    # Obtener todos los chats
    all_chats = querys.get_all_chats(skip=0, limit=10)

    # Verificar que se obtuvieron todos los chats
    assert len(all_chats) == 3
    assert all(isinstance(chat, Chat) for chat in all_chats)

    # Probar paginación
    paginated_chats = querys.get_all_chats(skip=1, limit=2)
    assert len(paginated_chats) == 2


def test_update_chat():
    db = next(get_db())
    querys = ChatQuerys(db=db)

    # Crear un chat para actualizar
    new_chat = querys.create_chat(id_scraped="old_id", last_text_url="http://old.com")

    # Actualizar el chat
    updated_chat = querys.update_chat(
        chat_id=new_chat.id,
        id_scraped="new_id",
        last_text_url="http://new.com"
    )

    # Verificar que el chat se actualizó correctamente
    assert updated_chat is not None
    assert updated_chat.id_scraped == "new_id"
    assert updated_chat.last_text_url == "http://new.com"

    # Verificar que los cambios persisten en la base de datos
    db_chat = querys.get_chat(chat_id=new_chat.id)
    assert db_chat.id_scraped == "new_id"
    assert db_chat.last_text_url == "http://new.com"

    # Intentar actualizar un chat inexistente
    non_existent_update = querys.update_chat(chat_id=9999, id_scraped="fail")
    assert non_existent_update is None


def test_delete_chat():
    db = next(get_db())
    querys = ChatQuerys(db=db)

    # Crear un chat para eliminar
    new_chat = querys.create_chat(id_scraped="to_delete")

    # Eliminar el chat
    deletion_result = querys.delete_chat(chat_id=new_chat.id)

    # Verificar que el chat fue eliminado
    assert deletion_result is True
    assert querys.get_chat(chat_id=new_chat.id) is None

    # Intentar eliminar un chat inexistente
    non_existent_deletion = querys.delete_chat(chat_id=9999)
    assert non_existent_deletion is False