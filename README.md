# User Authentication API
User microservice for authentication

This Flask application provides a comprehensive solution for user authentication, including support for email/password and Google OAuth-based logins. It leverages JWT (JSON Web Tokens) for secure, token-based user sessions, offering endpoints for user registration, login, and profile management.
Features

**User Registration and Login**: Users can sign up using their email and password, and log in to access protected endpoints.

**Google OAuth Integration**: Users can also log in using their Google account for a seamless authentication experience.

**JWT Session Management**: Secure token-based session management using JWT, with support for cookie storage of access tokens.

**User Profile Management**: Authenticated users can fetch, update, and delete their profile information.

Environment Setup

Before running the application, ensure you have the following environment variables set:

    JWT_SECRET_KEY: A secret key for JWT to sign the tokens.
    GOOGLE_CLIENT_ID: Your Google application client ID for OAuth.
    GOOGLE_CLIENT_SECRET: Your Google application client secret for OAuth.

Installation

    Clone the repository:

bash

git clone https://yourrepositoryurl.git

    Install the required packages:

bash

cd yourprojectdirectory
pip install -r requirements.txt

    Set up the necessary environment variables as described in the Environment Setup section.

    Run the application:

bash

flask run

Endpoints
User Registration

    Path: /api/user/register
    Method: POST
    Payload: JSON object with email, password, first_name, last_name.
    Description: Registers a new user with the given details.

User Login

    Path: /api/user/login
    Method: POST
    Payload: JSON object with email, password.
    Description: Authenticates the user and returns a JWT token.

Google OAuth Login

    Path: /api/user/login/google
    Method: GET
    Description: Redirects the user to Google for OAuth-based authentication.

Fetch User Profile

    Path: /api/user/
    Method: GET
    Description: Returns the profile information of the currently logged-in user.

Update User Profile

    Path: /api/user/
    Method: PUT
    Payload: JSON object with fields to update (username, first_name, last_name, password).
    Description: Updates the user's profile information.

Delete User

    Path: /api/user/
    Method: DELETE
    Description: Deletes the currently logged-in user's account.