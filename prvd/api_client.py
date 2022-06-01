'''API client base class.'''

#  Copyright 2017-2022 Provide Technologies Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import json
import os
import requests


class APIClient(object):

    DEFAULT_SCHEME = 'https'
    DEFAULT_VERSION = 'v1'

    def __init__(self, scheme, host, token):
        self.base_url = '{}://{}/api/{}'.format(scheme, host, APIClient.DEFAULT_VERSION)
        self.token = token

    def get(self, uri, params):
        r = requests.get('{}/{}'.format(self.base_url, uri), headers=self.__headers__(), params=params)
        response = r.text
        if r.status_code == 200 and r.headers['content-type'].find('application/json') == 0:
            response = r.json()
        return r.status_code, r.headers, response

    def post(self, uri, params):
        headers = self.__headers__()
        headers['content-type'] = 'application/json'
        r = requests.post('{}/{}'.format(self.base_url, uri), headers=headers, data=json.dumps(params))
        response = r.text
        if r.status_code < 300 and r.headers['content-type'].find('application/json') == 0:
            response = r.json()
        return r.status_code, r.headers, response

    def put(self, uri, params):
        headers = self.__headers__()
        headers['content-type'] = 'application/json'
        r = requests.put('{}/{}'.format(self.base_url, uri), headers=headers, data=json.dumps(params))
        response = r.text
        if r.status_code < 300 and r.headers['content-type'].find('application/json') == 0:
            response = r.json()
        return r.status_code, r.headers, response

    def delete(self, uri):
        r = requests.delete('{}/{}'.format(self.base_url, uri), headers=self.__headers__())
        response = r.text
        if r.status_code < 300 and r.headers['content-type'].find('application/json') == 0:
            response = r.json()
        return r.status_code, r.headers, response

    def __headers__(self):
        headers = {
            'user-agent': os.environ.get('API_USER_AGENT', 'provide-python client'),
        }
        if self.token != None:
            headers['authorization'] = 'bearer {}'.format(self.token)
        return headers
