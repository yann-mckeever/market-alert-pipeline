import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_USER=os.getenv("DB_USER", "yann_mle")
DB_PASSWORD=os.getenv("DB_PASSWORD", "market_secure_password")
DB_HOST=os.getenv("DB_HOST", "localhost")
DB_PORT=os.getenv("DB_PORT","5432")
DB_NAME=os.getenv("DB_NAME", "market_risk_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine=create_engine(DATABASE_URL,echo=False)

SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

def get_db():
    """  
    Générateur de session pour s'assurer que la connexion s'est faite proprement
    """
    db=SessionLocal()
    try:
        yield db
    finally :
        db.close()
