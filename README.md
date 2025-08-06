# Flask application with Google Login (OAuth2) and JWT Authentication 
A Flask application demonstrating OAuth2 authentication with Google Login and JWT token generation for API protection.

## Features

- Google OAuth2 authentication flow
- Session management for logged-in users
- JWT token generation and validation
- Protected API endpoints using JWT middleware

## Prominent Libraries/Packages Used

- oauthlib – Used to handle the OAuth2 authorization workflow.
- requests –  for making HTTP calls to Google’s APIs)
- jwt (PyJWT) – Used for creating and decoding JWT tokens.


## Configuration


1. ### Set up a Google OAuth2 project:
    To enable Google login, you must create a Google application in your Google account and configure the necessary permissions and redirect URIs. This setup is not covered in this tutorial, but you can easily find detailed guides online by searching for "Google OAuth2 setup."
Basic steps for google configurations are below.

   - Go to Google Cloud Console
   - Create a new project and configure OAuth consent screen
   - Create OAuth 2.0 credentials (Web application type)
   - Add authorized redirect URIs (e.g., https://localhost:5000/logincallback)
   
2. ### Create a .env file with your credentials:
        GOOGLE_CLIENT_ID = google_client_id
        GOOGLE_CLIENT_SECRET = google_client_secret
        FLASK_APP_ID = flask_secret_key

## Key Components
### AuthManager Class
The AuthManager class handles the complete OAuth2 workflow with Google.

#### Key Methods

1. __get_google_provider_cfg()
   * Private method that retrieves Google's OAuth2 endpoints dynamically
   * Uses the OpenID Connect discovery URL
   

2. get_authorization_url(redirect_url, state)
   * Generates the Google authorization URL
   * Parameters:
      * redirect_url: Callback URL after authorization
      * state: Security token to prevent CSRF
   * Scopes requested: openid, email, profile

3. get_access_token(code, authorization_response, redirect_url, state)
   * Exchanges authorization code for access token
   * Verifies state parameter for security
   * Uses Google's token endpoint

4. get_userinfo(token_response)
   * Retrieves user information using the access token
   * Verifies email address
   * Returns user profile (ID, email, name, picture)

### JWT Token Manager
* While JWTs aren't heavily used in this project, a middleware layer has been implemented to demonstrate how JWTs can be used to protect API routes.
1. create_jwt_access_token(user_login)
   * Generates JWT token for  user_login
2. decode_jwt_token(token)
   * Validate jwt token
   
### Authorization Middle Layer
* Provides middleware for protecting API endpoints. 
* It provides a decorator token_required which can be to protect apis by verifying a valid token. 

## Usage Flow
1. Login With Google link redirect the user /googlelogin
2. Application generates authorization URL with get_authorization_url()
3. User authenticates with Google
4. Google redirects to /logincallback with authorization code
5. Application exchanges code for tokens using get_access_token()
6. User info is retrieved with get_userinfo()
7. Session is established and JWT token generated

## Dependencies
    Flask
    oauthlib
    pyjwt
    python-dotenv
    requests