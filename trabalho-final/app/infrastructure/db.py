from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# TODO mover para variável de ambiente
DATABASE_URL = "mariadb+pymysql://root:mypass@localhost:3306/fastapi"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

