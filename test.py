from app.core.database import Base, engine
import app.models   # VERY IMPORTANT

print(Base.metadata.tables)

Base.metadata.create_all(bind=engine)

print("Tables created")