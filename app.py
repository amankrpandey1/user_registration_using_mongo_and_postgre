from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from uuid import uuid4
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import base64, bcrypt
from db import create_postgres_connection,create_mongo_connection


app = FastAPI()
templates = Jinja2Templates(directory="templates")

connection = create_postgres_connection()
mongo_db = create_mongo_connection()

@app.get('/')
def home():
    return {"message":"go to /user end point"}

def check_email_exists_in_postgres(email):
    try:
        connection = create_postgres_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        return result is not None
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error checking email in PostgreSQL")

def save_user_to_postgres(full_name, email, password, phone):
    try:
        connection = create_postgres_connection()
        cursor = connection.cursor()
        user_id = str(uuid4())


        cursor.execute("INSERT INTO users (id, first_name, password, email, phone) VALUES (%s, %s, %s, %s, %s)",
                       (user_id, full_name.split()[0], password, email, phone))
        connection.commit()
        cursor.close()
        connection.close()
        return user_id
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error saving user to PostgreSQL")

def save_profile_picture_to_mongo(user_id, profile_picture: UploadFile):

    try:
        mongo_collection = mongo_db['profile_pictures']
        file_content = profile_picture.file.read()
        mongo_collection.insert_one({'user_id': user_id, 'profile_picture': file_content})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error saving profile picture to MongoDB")
    
def get_all_users_from_postgres():
    try:
        connection = create_postgres_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        cursor.close()
        connection.close()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching users from PostgreSQL")

def get_user_from_postgres(user_id):
    try:
        connection = create_postgres_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        connection.close()
        return user_data
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching user data from PostgreSQL")

def get_user_profile_picture_from_mongo(user_id):
    try:
        mongo_collection = mongo_db['profile_pictures']
        result = mongo_collection.find_one({'user_id': user_id})
        if result:
            return result['profile_picture']
        else:
            raise HTTPException(status_code=404, detail="User profile picture not found in MongoDB")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching profile picture from MongoDB")


@app.get('/user/', response_model=list[dict])
def get_all_users():
    # Fetch all users from PostgreSQL
    users = get_all_users_from_postgres()
    
    # Convert the data to a list of dictionaries
    user_list = []
    for user_data in users:
        user_dict = {
            'user_id': user_data[0],
            'full_name': user_data[1],
            'password': user_data[2],
            'email': user_data[3],
            'phone': user_data[4]
        }
        user_list.append(user_dict)

    return user_list


@app.post('/user/')
def register_user(full_name: str, email: str, password: str, phone: str, profile_picture: UploadFile = File(...)):
    # Check if email already exists in PostgreSQL
    if check_email_exists_in_postgres(email):
        raise HTTPException(status_code=400, detail="Email already exists")

    # Save user data in PostgreSQL
    user_id = save_user_to_postgres(full_name, email, password, phone)

    # Save user profile picture in MongoDB
    save_profile_picture_to_mongo(user_id, profile_picture)

    return {"message": "User registered successfully"}


@app.get('/user/{user_id}', response_model=dict)
def get_registered_user_details(user_id: str):
    # Fetch user data from PostgreSQL
    user_data = get_user_from_postgres(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found in PostgreSQL")

    # user_data is a tuple from the query, convert it to dictionary for easier access
    user_data_dict = {
        'user_id': user_data[0],
        'full_name': user_data[1],
        'password': user_data[2],
        'email': user_data[3],
        'phone': user_data[4]
    }

    # Fetch user profile picture from MongoDB
    try:
        profile_picture = get_user_profile_picture_from_mongo(user_id)
    except HTTPException as e:
        if e.status_code == 404:
            profile_picture = None
        else:
            raise

    # If profile picture is available, encode it as base64
    if profile_picture:
        profile_picture_base64 = base64.b64encode(profile_picture).decode('utf-8')
        user_data_dict['profile_picture'] = profile_picture_base64
    else:
        user_data_dict['profile_picture'] = None

    return user_data_dict

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
