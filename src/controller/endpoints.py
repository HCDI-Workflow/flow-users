from flask import Flask, Blueprint, request, jsonify, redirect, url_for, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies
from authlib.integrations.flask_client import OAuth
from user import create_app
from resources import user_dao, user_dto
from resources.user_dao import UserDAO
from resources.user_dto import UserDTO
import os
from util.utils import hash_password, check_password

# app = create_app()
from user import create_app

app = create_app()

# Ensure environment variables are set
# required_env_vars = ["JWT_SECRET_KEY", "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"]
# for var in required_env_vars:
#     if not os.getenv(var):
#         raise EnvironmentError(f"Missing required environment variable: {var}")


jwt = JWTManager(app)

# Setup Google OAuth with environment variables
oauth = OAuth(app)
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
    client_kwargs={'scope': 'openid email profile'},
)

bp = Blueprint('user-endpoints', __name__, url_prefix='/api/user')


def auth_user_profile(access_token, user_dto_response):
    if user_dto_response is None:
        return {'error': "No User"}
    user_type = {
        'id': user_dto_response['id'],
        'username': user_dto_response['username'],
        'first_name': user_dto_response['first_name'],
        'last_name': user_dto_response['last_name'],
        'email': user_dto_response['email'],
        'auth_type': user_dto_response['auth_type']
    }
    return {'auth_token': access_token, 'user': user_type}


# Email + password
@bp.route('/register', methods=['POST'])
def create_user():
    data = request.get_json()  # get user data
    user_model = UserDTO.to_model(data)  # Parse and validate DTO

    if user_model is None:
        return {"error": "No User"}
    # Hash password
    user_model.password = hash_password(user_model.password)
    # Attempt to save model to database
    result = UserDAO.create_user(user_model)  # returns status and resource in dic

    created_user = result.get('resource')
    status = result['status']
    access_token = create_access_token(identity=created_user['id'])

    # user_profile = UserDTO.from_model(created_user)
    safe_to_return = auth_user_profile(access_token, created_user)


    # format response
    if app.config['JWT_TOKEN_LOCATION'] == ['cookies']:
        response = make_response(jsonify(safe_to_return), 201)
        set_access_cookies(response, access_token)  # include access_token as cookie
    else:
        response = make_response(jsonify(safe_to_return), 201)

    return response


@bp.route('/login', methods=['POST'])
def login_user():
    """
    Login using email password
    """
    data = request.get_json()

    # Make sure fields are there
    required_fields = ['email', 'password']
    for field in required_fields:
        if field not in data.keys():
            return {'error': "Invalid fields"}, 400

    # Continue after checks
    user = UserDAO.get_user_by_credentials(data['email'], data['password'])

    if user:
        access_token = create_access_token(identity=user.id)
        user_dto_response = UserDTO.from_model(user)

        auth_user = auth_user_profile(access_token, user_dto_response)
        # Use if just want logged in confirmation
        response = make_response(jsonify(auth_user), 200)

        if app.config['JWT_TOKEN_LOCATION'] == ['cookies']:
            set_access_cookies(response, access_token)  # Set the JWT as a cookie in the response
        return response
    return {'error': 'Invalid credentials'}, 401


# Google OAUTH
@bp.route('/login/google')
def google_login():
    """

    Called when user clicks "Login with google" button on front end

    Initiates the Google SSO login process. This function generates a redirect
    URI for the Google OAuth service and redirects the user to Google's OAuth
    server to begin the authentication process.

    Route: /login/google
    Method: GET
    Response: Redirects to Google's OAuth 2.0 server for user authentication.
    """
    redirect_uri = url_for('user-endpoints.google_authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@bp.route('/login/google/authorize')
def google_authorize():
    """

    Handles the callback from Google OAuth after user authentication. This function
    exchanges the authorization code for an access token internally and retrieves 
    the user's profile information from Google. It then checks if the user exists 
    in the application's database or creates a new user record. Finally, it generates 
    a JWT for the authenticated user.

    Route: /login/google/authorize
    Method: GET
    Response: JSON response containing the JWT for the authenticated user.
    """
    # oauth.google.authorize_access_token()  # Exchange authorization code for access token
    # userinfo = oauth.google.get('userinfo').json()  # Retrieve user information
    # user = UserDAO.get_or_create_user_by_google_info(userinfo)
    # access_token = create_access_token(identity=user.id)  # Generate JWT token for the user
    # return jsonify(access_token=access_token)
    oauth.google.authorize_access_token()  # Exchange authorization code for access token
    userinfo = oauth.google.get('userinfo').json()  # Retrieve user information
    user = UserDAO.get_or_create_user_by_google_info(userinfo)

    # Check if user is successfully retrieved or created
    if user:
        access_token = create_access_token(identity=user.id)
        user_dto_response = UserDTO.from_model(user)
        # Use if just want logged in confirmation
        response = make_response(jsonify(logged_in_as=user_dto_response['username'],
                                         first_name=user_dto_response['first_name'],
                                         last_name=user_dto_response['last_name'],
                                         email=user_dto_response['email'],
                                         auth_type=user_dto_response['auth_type'],
                                         auth_token=access_token), 200)

        if app.config['JWT_TOKEN_LOCATION'] == ['cookies']:
            set_access_cookies(response, access_token)  # Set the JWT as a cookie in the response
        return response

    return jsonify(error='Authentication failed'), 401


@bp.route('/', methods=['GET'])
@jwt_required()
def get_user():
    """
    For all non-profile updating/creating calls.

    """

    current_user_id = get_jwt_identity()  # decodes token
    user = UserDAO.get_user_by_id(current_user_id)  # user is a dict

    if user:
        user_dto_response = UserDTO.from_model(user)  # Convert to DTO
        response = jsonify(username=user_dto_response['username'],
                           first_name=user_dto_response['first_name'],
                           last_name=user_dto_response['last_name'],
                           email=user_dto_response['email'],
                           auth_type=user_dto_response['auth_type'],
                           id=user_dto_response['id']
                           )
        return response, 200

    return jsonify(error='User not found'), 404


@bp.route('/', methods=['PUT'])
@jwt_required()
def update_user():
    """
    Updates the information of the currently logged-in user. 

    Returns the user info after updated
    """
    data = request.get_json()  # user inputed updates
    allowed_fields = ['username', 'first_name', 'last_name', 'password']

    for field in data.keys():
        if field not in allowed_fields:
            return {'error': "Invalid input"}, 400

    current_user_id = get_jwt_identity()  # get id of user
    user_current = UserDAO.get_user_by_id(current_user_id)  # user model currently
    user_dto_response = UserDTO.from_model(user_current)  # convert to dict
    original = user_dto_response.copy()  # save incase needed for failure to update

    # Update
    for key, value in data.items():
        if key == 'password':
            user_dto_response[key] = hash_password(value)
        else:
            user_dto_response[key] = value

    user_updated_bool = UserDAO.update_user(current_user_id, user_dto_response)  # update user
    if user_updated_bool:
        response = jsonify(username=user_dto_response['username'],
                           first_name=user_dto_response['first_name'],
                           last_name=user_dto_response['last_name'],
                           email=user_dto_response['email'],
                           auth_type=user_dto_response['auth_type'],
                           id=user_dto_response['id']
                           )
        return response, 200

    return jsonify(error=f"Failed to update {original['username']}'s account"), 404


@bp.route('/', methods=['DELETE'])
@jwt_required()
def delete_user():
    """
    COMPLETED
    Deletes the currently logged-in user. The user's identity is extracted from the JWT token.

    Return message states username and email
    """
    current_user_id = get_jwt_identity()
    current_user_obj = UserDAO.get_user_by_id(current_user_id)
    if not current_user_obj:
        return {'error': 'User does not exist'}, 404

    UserDAO.delete_user(current_user_id)
    return {
        'message': f'Account for {current_user_obj.username} with email {current_user_obj.email} deleted successfully'}, 200


app.register_blueprint(bp)
