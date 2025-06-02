from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid
from sqlalchemy.orm import Session


Base = declarative_base()


class UserAccount(Base):
    __tablename__ = 'user_useraccount'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    external_id = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(255))
    last_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_staff = Column(Boolean, default=False)
    role = Column(String(10), default='consultant')
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    posts = relationship("Post", back_populates="user")
    comments = relationship("Comment", back_populates="user")

    def save(self, db: Session):
        if not self.external_id:
            self.external_id = f"user_{uuid.uuid4().hex}"
        db.add(self)
        db.commit()
        db.refresh(self)


class Post(Base):
    __tablename__ = 'post_post'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    external_id = Column(String(50), unique=True, nullable=False)
    content = Column(String(200), nullable=False)
    user_id = Column(Integer, ForeignKey('user_useraccount.id'), nullable=False)
    source_id = Column(Integer, ForeignKey('source_source.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    user = relationship("UserAccount", back_populates="posts")
    source = relationship("Source", back_populates="posts")
    comments = relationship("Comment", back_populates="post")

    def __repr__(self):
        return f"Post(content='{self.content}', created_at='{self.created_at}')"

    def save(self, db: Session):
        if not self.external_id:
            unique_id = uuid.uuid4().hex
            self.external_id = f"post_{unique_id}"
        db.add(self)
        db.commit()
        db.refresh(self)



class UserOwner(Base):
    __tablename__ = "comment_user_owner_userowner"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    external_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones inversas si las necesitas
    conversations = relationship("Conversation", back_populates="user")
    comments = relationship("Comment", back_populates="user_owner")

    def __repr__(self):
        return f"UserOwner(name='{self.name}', created_at='{self.created_at}')"

    def save(self, db: Session):
        if not self.external_id:
            unique_id = uuid.uuid4().hex
            self.external_id = f"usro_{unique_id}"
        db.add(self)
        db.commit()
        db.refresh(self)


class Conversation(Base):
    __tablename__ = "messenger_conversation"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    messenger_id = Column(String(255), primary_key=True, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("comment_user_owner_userowner.id"), nullable=True)
    link = Column(String(100), nullable=False)
    messenger_updated_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    user = relationship("UserOwner", back_populates="conversations")
    comments = relationship("Comment", back_populates="messenger_conversation")

    def __repr__(self):
        return f"Conversation(messenger_id='{self.messenger_id}', user={self.user.name if self.user else 'None'})"

    def save(self, db: Session):
        db.add(self)
        db.commit()
        db.refresh(self)

class Comment(Base):
    __tablename__ = "comment_comment"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    external_id = Column(String(50), unique=True, nullable=False, index=True)
    messenger_id = Column(String(255), unique=True, nullable=True)
    text = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("user_useraccount.id"), nullable=True)  # Assuming UserAccount model is "users"
    user_owner_id = Column(Integer, ForeignKey("comment_user_owner_userowner.id"), nullable=True)
    post_id = Column(Integer, ForeignKey("post_post.id"), nullable=True)
    classification_id = Column(Integer, ForeignKey("classification_classification.id"), nullable=True)
    source_id = Column(Integer, ForeignKey("source_source.id"), nullable=True)
    messenger_conversation_id = Column(String(50), ForeignKey("messenger_conversation.messenger_id"))
    messenger_created_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    user = relationship("UserAccount", foreign_keys=[user_id], back_populates="comments")
    user_owner = relationship("UserOwner", foreign_keys=[user_owner_id], back_populates="comments")
    post = relationship("Post", foreign_keys=[post_id], back_populates="comments")
    classification = relationship("Classification", foreign_keys=[classification_id], back_populates="comments")
    source = relationship("Source", foreign_keys=[source_id], back_populates="comments")
    messenger_conversation = relationship("Conversation", foreign_keys=[messenger_conversation_id], back_populates="comments")

    def __repr__(self):
        return f"Comment(text='{self.text[:20]}...', created_at='{self.created_at}')"

    def save(self, db: Session):
        if not self.external_id:
            self.external_id = f"comm_{uuid.uuid4().hex}"
        db.add(self)
        db.commit()
        db.refresh(self)


class Classification(Base):
    __tablename__ = 'classification_classification'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    external_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    classification_type = Column(String(100), default="default_type")

    # Relación uno-a-muchos: una clasificación tiene muchos comentarios
    comments = relationship("Comment", back_populates="classification")

    def __repr__(self):
        return f"Classification(name='{self.name}', type='{self.classification_type}', created_at='{self.created_at}')"

    def save(self, db: Session):
        if not self.external_id:
            unique_id = uuid.uuid4().hex
            self.external_id = f"clas_{unique_id}"
        db.add(self)
        db.commit()
        db.refresh(self)



class Source(Base):
    __tablename__ = 'source_source'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    external_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(String(200))
    url = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    posts = relationship("Post", back_populates="source")

    comments = relationship(
        "Comment",
        foreign_keys=[Comment.source_id],
        back_populates="source"
    )

    def __repr__(self):
        return f"Source(name='{self.name}', url='{self.url}', created_at='{self.created_at}')"

    def save(self, db: Session):
        if not self.external_id:
            unique_id = uuid.uuid4().hex
            self.external_id = f"src_{unique_id}"
        db.add(self)
        db.commit()
        db.refresh(self)
