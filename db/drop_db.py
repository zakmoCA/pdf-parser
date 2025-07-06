import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from models import Base

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def drop():
    Base.metadata.drop_all(engine)
    print("All tables dropped.")

if __name__ == "__main__":
    drop()
