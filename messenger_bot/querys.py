# crud/user_owner.py
from sqlalchemy.orm import Session
from .models import UserOwner, Comment, Conversation, Source
import uuid
from datetime import datetime

# User Owner CRUD
def get_user_owner_by_id(db: Session, user_id: int):
    return db.query(UserOwner).filter(UserOwner.id == user_id).first()

def get_user_owner_by_name(db: Session, name: str):
    return db.query(UserOwner).filter(UserOwner.name == name).first()

def get_user_owners(db: Session, skip: int = 0, limit: int = 100):
    return db.query(UserOwner).offset(skip).limit(limit).all()

def create_user_owner(db: Session, name: str):
    db_user = UserOwner(name=name)
    db_user.save(db)  # Usamos el método save personalizado
    return db_user

def update_user_owner(db: Session, user_id: int, new_name: str):
    db_user = db.query(UserOwner).filter(UserOwner.id == user_id).first()
    if db_user:
        db_user.name = new_name
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user_owner(db: Session, user_id: int):
    db_user = db.query(UserOwner).filter(UserOwner.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user


 # Conversation CRUD
def get_conversation(db: Session, messenger_id: str):
    return db.query(Conversation).filter(Conversation.messenger_id == messenger_id).first()

def get_all_conversations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Conversation).offset(skip).limit(limit).all()

def create_conversation(
    db: Session,
    user_owner_id: int,
    link: str,
    messenger_updated_at: datetime,
    messenger_id: str = None
):
    if not messenger_id:
        messenger_id = f"conv_{uuid.uuid4().hex}"
    
    db_conversation = Conversation(
        messenger_id=messenger_id,
        user_id=user_owner_id,
        link=link,
        messenger_updated_at=messenger_updated_at
    )
    db_conversation.save(db)
    return db_conversation

def update_conversation_link(
    db: Session,
    messenger_id: str,
    new_link: str
):
    db_conversation = get_conversation(db, messenger_id)
    if db_conversation:
        db_conversation.link = new_link
        db.commit()
        db.refresh(db_conversation)
    return db_conversation

def delete_conversation(db: Session, messenger_id: str):
    db_conversation = get_conversation(db, messenger_id)
    if db_conversation:
        db.delete(db_conversation)
        db.commit()
    return db_conversation

def get_comments_by_conversation(db: Session, messenger_id: str, skip: int = 0, limit: int = 100):
    return (
        db.query(Comment)
        .join(Conversation)
        .filter(Comment.conversation_id == messenger_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


# Message CRUD
def get_comment(db: Session, external_id: str):
    return db.query(Comment).filter(Comment.external_id == external_id).first()

def get_comments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Comment).offset(skip).limit(limit).all()

def create_comment(
    db: Session,
    text: str,
    user_owner_id: int,
    conversation_id: str,
    user_id: int = None,
    post_id: int = None,
    classification_id: int = None,
    source_id: int = None,
    messenger_created_at: datetime = None,
    messenger_id: str = None
):
    db_comment = Comment(
        text=text,
        user_id=user_id,
        user_owner_id=user_owner_id,
        post_id=post_id,
        classification_id=classification_id,
        source_id=source_id,
        messenger_conversation_id=conversation_id,
        messenger_id=messenger_id,
        messenger_created_at=messenger_created_at or datetime.utcnow()
    )
    db_comment.save(db)
    return db_comment

def update_comment_text(db: Session, external_id: str, new_text: str):
    db_comment = get_comment(db, external_id)
    if db_comment:
        db_comment.text = new_text
        db.commit()
        db.refresh(db_comment)
    return db_comment

def delete_comment(db: Session, external_id: str):
    db_comment = get_comment(db, external_id)
    if db_comment:
        db.delete(db_comment)
        db.commit()
    return db_comment

def get_comments_by_user_owner(db: Session, user_owner_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(Comment)
        .filter(Comment.user_owner_id == user_owner_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_comments_by_post(db: Session, post_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(Comment)
        .filter(Comment.post_id == post_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_comment_by_messenger_and_conversation(
    db: Session,
    messenger_id: str,
    conversation_id: int,
    skip: int = 0,
    limit: int = 100
):
    # print(f"get_comment_by_messenger_and_conversation: messenger_id={messenger_id}, conversation_id={conversation_id}")

    return (
        db.query(Comment)
        .filter(
            Comment.messenger_id == messenger_id,
            Comment.messenger_conversation_id == conversation_id
        )
        .offset(skip)
        .limit(limit)
        .first()
    )


# Source CRUD
def get_source_by_id(db: Session, source_id: int):
    return db.query(Source).filter(Source.id == source_id).first()

def get_source_by_name(db: Session, name: str):
    return db.query(Source).filter(Source.name == name).first()

def get_sources(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Source).offset(skip).limit(limit).all()

def create_source(
    db: Session,
    name: str,
    description: str,
    url: str,
    created_at: datetime,
    external_id: str = None
):
    db_source = Source(
        name=name,
        description=description,
        url=url,
        created_at=created_at,
        external_id=external_id
    )
    db_source.save(db)
    return db_source

def update_source_name(
    db: Session,
    source_id: int,
    new_name: str
):
    db_source = get_source_by_id(db, source_id)
    if db_source:
        db_source.name = new_name
        db.commit()
        db.refresh(db_source)
    return db_source

def delete_source(db: Session, source_id: int):
    db_source = get_source_by_id(db, source_id)
    if db_source:
        db.delete(db_source)
        db.commit()
    return db_source