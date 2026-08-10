from app.database.database import Base, engine
import app.models

Base.metadata.create_all(bind=engine)

print("Database and tables created successfully!")