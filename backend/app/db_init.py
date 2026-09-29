from app.db import Base, engine
import app.models  # noqa: F401
from app.seed_data import seed_database


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("DealDNA database tables created.")
    seed_database()
