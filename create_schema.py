from db import create_postgres_connection,create_mongo_connection


def create_postgres_tables():
    try:
        connection = create_postgres_connection()
        cursor = connection.cursor()

        # Create the 'users' table in PostgreSQL
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                password VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone VARCHAR(20) NOT NULL
            )
        """)

        connection.commit()
        cursor.close()
        connection.close()
        print("PostgreSQL table created successfully.")
    except Exception as e:
        print("Error creating PostgreSQL tables:", e)

def create_mongo_collections():
    try:
        # Create the 'profile_pictures' collection in MongoDB
        mongo_db = create_mongo_connection()
        mongo_db.create_collection('profile_pictures')
        print("MongoDB collection created successfully.")
    except Exception as e:
        print("Error creating MongoDB collection:", e)

if __name__ == '__main__':
    create_postgres_tables()
    create_mongo_collections()
