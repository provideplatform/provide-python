'''API client for the ident.provide.services microservice.'''

from api_client import APIClient

class Ident(APIClient):

    DEFAULT_HOST = 'ident.provide.services'

    def __init__(self, token):
        super(Ident, self).__init__(APIClient.DEFAULT_SCHEME, Ident.DEFAULT_HOST, token) 
        
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
