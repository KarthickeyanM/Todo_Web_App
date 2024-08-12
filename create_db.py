from models import Base, engine

def create_database():
    Base.metadata.create_all(engine)
    print("Database and tables created successfully.")

if __name__ == '__main__':
    create_database()
