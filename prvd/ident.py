'''API client for the ident.provide.services microservice.'''

import os

from api_client import APIClient


class Ident(APIClient):

    DEFAULT_HOST = 'ident.provide.services'

    def __init__(self, token):
        scheme = os.environ.get('IDENT_API_SCHEME', Ident.DEFAULT_SCHEME)
        host = os.environ.get('IDENT_API_HOST', Ident.DEFAULT_HOST)
        super(Ident, self).__init__(scheme, host, token) 
        
    def create_application(self, params):
        return self.post('applications', params)

    def update_application(self, app_id, params):
        return self.put('applications/{}'.format(app_id), params)

    def fetch_applications(self, params):
        return self.get('applications', params)

    def fetch_application_details(self, app_id):
        return self.get('applications/{}'.format(app_id), {})

    def fetch_application_tokens(self, app_id):
        return self.get('applications/{}/tokens'.format(app_id), {})

    def authenticate(self, params):
        return self.post('authenticate', params)

    def fetch_tokens(self, params):
        return self.get('tokens', params)

    def fetch_token_details(self, token_id):
        return self.get('tokens/{}'.format(token_id), {})

    def delete_token(self, token_id):
        return self.delete('tokens/{}'.format(token_id))

    def create_user(self, params):
        return self.post('users', params)

    def fetch_users(self):
        return self.get('users', {})

    def fetchUserDetails(self, user_id):
        return self.get('users/{}'.format(user_id), {})

    def update_user(self, user_id, params):
        return self.put('users/{}'.format(user_id), params)

    def create_kyc_application(self, params):
        return self.post('kyc_applications', params)

    def update_kyc_application(self, app_id, params):
        return self.put('kyc_applications/{}'.format(app_id), params)

    def fetch_kyc_applications(self, params):
        return self.get('kyc_applications', params)

    def fetch_kyc_application_details(self, kyc_app_id):
        return self.get('kyc_applications/{}'.format(kyc_app_id), {})
