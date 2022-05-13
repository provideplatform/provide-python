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

import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='prvd',
    version='0.2.1',
    author='Kyle Thomas',
    author_email='kyle@provide.services',
    description='Provide python client',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/provideservices/provide-python',
    packages=setuptools.find_packages(),
    install_requires=[
        'ipfshttpclient',
        'pyjwt',
        'requests',
    ],
    classifiers=[
    ],
)
