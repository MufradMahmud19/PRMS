import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import OperationalError

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'hospital.db')

def test_sqlite_db(path):
    if not os.path.exists(path):
        print("❌ Database file does not exist:", path)
        return

    print("✅ Database file exists:", path)

    engine = create_engine(f"sqlite:///{path}")
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"✅ Connected successfully. Found tables: {tables if tables else 'None'}")
    except OperationalError as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_sqlite_db(db_path)