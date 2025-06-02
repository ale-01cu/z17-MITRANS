from fastapi import FastAPI, Depends
import time
from .db import SessionLocal, engine
from .models import Base
import logging
from .tasks import messenger_api_task
from .querys import get_all_conversations

app = FastAPI()

# Crear todas las tablas definidas en los modelos
def init_db():
    Base.metadata.create_all(bind=engine)

init_db()

# Dependencia para obtener una sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db = next(get_db())

logging.basicConfig(
    level=logging.INFO,
    format='INFO:     %(message)s',
    handlers=[logging.StreamHandler()]
)

allc = get_all_conversations(db=db)
print(allc)

while True:
  print("Running tasks...")

  messenger_api_task(db=db)

  time.sleep(5)