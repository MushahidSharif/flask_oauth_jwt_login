import os
import requests
import json
import dotenv

dotenv.load_dotenv()

from oauthlib.oauth2 import WebApplicationClient

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)

GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"


class AuthManager():
    """
    This class provides function to manage and perform OpenAuth work flow using oauthlib package.
    Note: requests-oauthlib package might be simpler to use for this but we are using oauthlib to understand complete workflow used in authorization
    """
    def __init__(self):
        pass

    def __get_google_provider_cfg(self):
        """
        returns json object containing various info and endpoints related to authorization from google.
        Instead of using hardcode urls we should get the urls from discovery url.
        """

        return requests.get(GOOGLE_DISCOVERY_URL).json()

    def get_authorization_url(self, redirect_url, state):
        """
        prepare a url string for google authorization with the required data.

        :param redirect_url: url which google authorization server will redirect to after successful user/pass verification.
        :param state: Some value which will sent to auth server and it will be sent back to the redirect_url from server. This can be used to verify that
        server response is valid and coming from the same workflow.
        """

        # Get google's authorization URL to perform login
        google_provider_cfg = self.__get_google_provider_cfg()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]

        client = WebApplicationClient(GOOGLE_CLIENT_ID)
        # Construct and send the request for Google login and provide scopes to retrieve  user's profile from Google
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=redirect_url,
            scope=["openid", "email", "profile"],
            state = state,
            prompt = 'select_account'
        )
        return request_uri

    def get_access_token(self, code, authorization_response, redirect_url, state):
        """
        Get and return the access token from google

        :param code: code that is sent back by google after authorization
        :param authorization_response: response that was sent back from google's authorization url.
        :param redirect_url: original redirect url that was provided to google authorization url.
        :param state: state which is sent by auth server (google) to the callback url. If it is not same as the state that was sent with the request to
        authorization_url then it is not the same workflow and it access token call will fail.
        :return:
        """

        # Retrieve endpoint to get access token
        google_provider_cfg = self.__get_google_provider_cfg()
        token_endpoint = google_provider_cfg["token_endpoint"]

        client = WebApplicationClient(GOOGLE_CLIENT_ID)
        # Prepare and send a request to get tokens
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=authorization_response,
            redirect_url=redirect_url,
            state=state
        )
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )

        return token_response

    def get_userinfo(self, token_response):

        client = WebApplicationClient(GOOGLE_CLIENT_ID)
        access_token = client.parse_request_body_response(json.dumps(token_response.json()))

        google_provider_cfg = self.__get_google_provider_cfg()
        # We have the access token. Now get user profile using this token
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)

        # if email is verified then user authenticated with Google.
        if userinfo_response.json().get("email_verified"):
            unique_id = userinfo_response.json()["sub"]
            users_email = userinfo_response.json()["email"]
            picture = userinfo_response.json()["picture"]
            users_name = userinfo_response.json()["given_name"]
            # return userinfo_response.json()
            return userinfo_response
        else:
            return None
