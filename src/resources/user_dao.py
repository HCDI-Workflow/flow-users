# src/resources/user_dao.py

from model.user import User
from flask_sqlalchemy import SQLAlchemy
import logging
from util.utils import check_password
import sqlalchemy
from sqlalchemy import text
from resources.user_dto import UserDTO
from user.db import DatabaseManager



manager = DatabaseManager()
logger = logging.getLogger()


db = SQLAlchemy()

def get_user_by_email(email):
    engine = manager.connect_with_connector()

    query = sqlalchemy.text("SELECT * FROM users WHERE email = :email;")
    with engine.connect() as connection:
        # result = connection.execute(query, {'email': email}).fetchall()

        row = connection.execute(query, {'email': email}).fetchone()
        # return(str(type(row)))
        # Convert RowProxy to a dictionary
        if row is not None:
            user = row._asdict()
        else:
            user = None
    # return result 
    return user


    # return result > 0  # Returns True if user exists, False otherwise

class UserDAO:

    @staticmethod
    def get_user_by_id(user_id):
        """
        Retrieve a single user by their ID.

        Returns a user instance
        """
        
        engine = manager.connect_with_connector()

        query = sqlalchemy.text("SELECT * FROM users WHERE id = :id;")
        with engine.connect() as connection:
            row = connection.execute(query, {'id': user_id}).fetchone()

            # return(str(type(row)))
            # Convert RowProxy to a dictionary
            if row is not None:
                user = row._asdict()
            else:
                user = None

        if row is None:
            return None  # No user found with the given ID

        # Assuming the User class has a constructor that accepts keyword arguments
        # corresponding to its attributes
        return User(
            id=user['id'],
            username=user['username'],
            email=user['email'],
            first_name=user['first_name'],
            last_name=user['last_name'],
            password=user['password'],
            auth_type=user['auth_type']
        )

    
    @staticmethod
    def create_user(user):

        """
        Creates user:
        Input: 
        - user (class user object)
        Output:
        - dict (status and resource). resource is a dictionary, status is a string       
        
        """
        engine = manager.connect_with_connector()

        # SQL query to insert a new user and return the created record
        query = sqlalchemy.text("""
            INSERT INTO users (username, email, first_name, last_name, password,  auth_type) 
            VALUES (:username, :email, :first_name, :last_name, :password, :auth_type)
            RETURNING *;
        """)
  
        user_data = UserDTO.from_model(user)
        # check if user exists
        result_dict = get_user_by_email(user_data['email'])
        exist_bool = (result_dict is not None)
        if exist_bool:
            return {'status': 'User already exists', 'resource':result_dict}

        # If user doesn't exist
        try:
            with engine.connect() as connection:
                row = connection.execute(query, user_data).fetchone()
                # row = connection.execute(query, {'id': user_id}).fetchone()
                if row is not None:
                    result_dict = row._asdict()
                else:
                    result = None
                connection.commit()  # Commit the transaction
                return {'status': f"Success. Created user with id = {result_dict['id']}", 'resource': result_dict}
        except Exception as e:
            # If an error occurs, rollback the transaction
            if connection:
                connection.rollback()
            return {'error': str(e), 'resource': None, 'status': 500}
        finally:
            if engine:
                engine.dispose()  # Properly close the connection

    @staticmethod

    def update_user(user_id, user_data):
        """
        Update an existing user's details.
        """
        engine = manager.connect_with_connector()
        query = sqlalchemy.text(f"""
            UPDATE users SET 
            username = :username, 
            first_name = :first_name,
            last_name = :last_name, 
            password = :password
            WHERE id = :id;
        """)
        try:
            with engine.connect() as connection:
                connection.execute(query, user_data)
                connection.commit()
                return True
        except Exception as e:
            # If an error occurs, rollback the transaction
            if connection:
                connection.rollback()
            return {'error': str(e)}
        finally:
            if engine:
                engine.dispose()  # Properly close the connection


    @staticmethod
    def delete_user(user_id):
        """
        Delete a user from the database.
        """
        engine = manager.connect_with_connector()
        query = sqlalchemy.text("DELETE FROM users WHERE id = :id;")
        try:
            with engine.connect() as connection:
                connection.execute(query, {'id': user_id})
                connection.commit() #ensure
                return True
        except Exception as e:
            # If an error occurs, rollback the transaction
            if connection:
                connection.rollback()
            return {'error': str(e)}
        finally:
            if engine:
                engine.dispose()
        
    
    @staticmethod
    def get_user_by_credentials(email, password):
        """
        Retrieve a user by their email and password.

        Returns as None or as a user model
        """
        engine = manager.connect_with_connector()

        query = sqlalchemy.text("SELECT * FROM users WHERE email = :email;")
        with engine.connect() as connection:
            row = connection.execute(query, {'email': email}).fetchone()
            # return(str(type(row)))
            # Convert RowProxy to a dictionary
            if row is not None:
                user = row._asdict()
            else:
                user = None

            # return list(user.keys())
            if user and check_password(password, user['password']):
                user['password'] = None # To avoid sending back password
                return User(
                    id=user['id'],
                    username=user['username'],
                    email=user['email'],
                    first_name=user['first_name'],
                    last_name=user['last_name'],
                    password=user['password'],
                    auth_type=user['auth_type']
                )
        return None
    

    @staticmethod
    def get_or_create_user_by_google_info(google_info):
        """
        Retrieves a user by their Google information. If the user does not exist,
        creates a new user in the database with the provided Google information.
        """
        database_manager = DatabaseManager()
        engine = database_manager.connect_with_connector()

        query_find_user = sqlalchemy.text("SELECT * FROM users WHERE email = :email;")
        user_data = {'email': google_info['email']}

        with engine.connect() as connection:
            user = connection.execute(query_find_user, user_data).fetchone()
            
            if user:
                return user
                # return {key: user[key] for key in user.keys()}
            
            query_create_user = sqlalchemy.text("""
                INSERT INTO users (username, email, name, oath_token, auth_type) 
                VALUES (:email, :email, :name, :oath_token, 'sso');
            """)
            
            new_user_data = {
                'email': google_info['email'],
                'name': google_info.get('name', ''),
                'oath_token': google_info.get('oauth_token', '')
            }
            
            connection.execute(query_create_user, new_user_data)
            new_user = connection.execute(query_find_user, {'email': google_info['email']}).fetchone()
            connection.commit()
            return new_user if new_user else None

