from sqlalchemy import text, Table, MetaData
from flask import Flask, request, jsonify, session
from models import User, session_db, engine, UserSession
import bcrypt
from flask_cors import CORS
from token_key import generate_token_key
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = f"{os.environ['SECRET_KEY']}"
CORS(app, resources={r"/api/*": {"origins":"*"}})

# Configure CORS to allow requests from specific domains
#cors = CORS(app, resources={r"/api/*": {"origins": ["https://example.com", "https://api.example.com"]}})

@app.route("/api/create_user", methods = ["POST"])
def create_user():
    data = request.json
    username, password, email, role = data.get('username'), data.get('password'), data.get('email'), data.get('role')
    existing_user = session_db.query(User).filter_by(username=username).first()
    if existing_user:
        return jsonify({'message' : 'User already exists'}), 409
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    new_user = User(username=username, password = hashed_password, email = email, role = role)
    session_db.add(new_user)
    session_db.commit()
    return jsonify({'message' : 'User created successfully'}), 201

@app.route("/api/login_user", methods = ['POST'])
def login_user():
    data = request.json
    username, password, role = data.get('username'), data.get('password'), data.get('role')
    existing_user = session_db.query(User).filter_by(username=username).first() 
    if existing_user and bcrypt.checkpw(password.encode('utf-8'), existing_user.password.encode('utf-8')):
        session_token = generate_token_key()
        session_tbl = UserSession(user_id=existing_user.id, token = session_token)
        session_db.add(session_tbl)
        session_db.commit()
        session['token'] = session_token
        return jsonify({'message' : "Login successfully", 'userId': existing_user.id}), 200
    else:
        return jsonify({'message' : 'Try again with valid credentials'}), 403
    

@app.route("/api/logout_user", methods = ['POST'])
def logout_user():
    user_session_token = session.get('token') # Get the loggedin user session token
    if user_session_token:
        session_token_db = session_db.query(UserSession).filter_by(token=user_session_token).first()
        if session_token_db:
            session_token_db.logout_time = datetime.now() # set the logout time and commit the changes
            session_db.commit()           
            session.pop('token', None) # Clear the session token from the user's session
            return jsonify({'message':'User logged out successfully'}), 200
        else:
            return jsonify({'message':'Invalid session token'}), 403
    else:
        return jsonify({'message' : 'Session token is not provided to user'}), 400
        
@app.route("/api/meta_analysis", methods = ['GET'])
def get_data_from_meta():
    #We can use text module for passing select * from meta_analysis
    metadata = MetaData()
    meta_analysis = Table('meta_analysis', metadata, autoload_with=engine)
    select_query = meta_analysis.select()
    with engine.connect() as connection:
        result = connection.execute(select_query)
        rows = result.fetchall()
    connection.close()

    # Get the column names
    column_names = meta_analysis.columns.keys()    
    if column_names and rows:
        #Create a list of dictionaries with column headers as keys
        data_with_headers = [dict(zip(column_names, row)) for row in rows]
        return jsonify({"meta_data" : data_with_headers}), 200
    else:
        return jsonify({"Error": "Metadata not available"}), 403


if __name__ == '__main__':
    app.run(debug=True, host='localhost')
