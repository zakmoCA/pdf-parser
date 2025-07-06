import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

def init_db():
    Base.metadata.create_all(engine)
    print("Database initialised.")

if __name__ == "__main__":
    init_db()
