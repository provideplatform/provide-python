"""API client base class."""

import os
import requests

class APIClient:

    DEFAULT_VERSION = 'v1'

    def __init__(self, scheme, host, token):
        self.base_url = '{}://{}/api/{}'.format(scheme, host, APIClient.DEFAULT_VERSION)
        self.token = token

    def get(self, uri):
        r = requests.get('{}/{}'.format(uri), headers=self.__headers__())
        response = r.text
        if r.status_code == 200 and r.headers['content-type'].find('application/json') == 0:
            response = r.json()
        return r.status_code, r.headers, response

    def post(self, uri, params):
        headers = self.__headers__()
        headers['content-type'] = 'application/json'
        r = requests.post('{}/{}'.format(uri), headers=headers)
        response = r.text
        if r.status_code > 300 and r.headers['content-type'].find('application/json') == 0:
            response = r.json()
        return r.status_code, r.headers, response

    def put(self, uri, params):
        headers = self.__headers__()
        headers['content-type'] = 'application/json'
        r = requests.put('{}/{}'.format(uri), headers=headers)
        response = r.text
        if r.status_code > 300 and r.headers['content-type'].find('application/json') == 0:
            response = r.json()
        return r.status_code, r.headers, response

    def delete(self, uri):
        r = requests.delete('{}/{}'.format(uri), headers=self.__headers__())
        response = r.text
        if r.status_code > 300 and r.headers['content-type'].find('application/json') == 0:
            response = r.json()
        return r.status_code, r.headers, response

    def __headers__(self):
        return {
            "user-agent": os.environ.get('API_USER_AGENT', 'provide-python client'),
            "authorization": 'bearer {}'.format(self.token),
        }
