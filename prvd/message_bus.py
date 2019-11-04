'''API client for the provide.services message bus microservice architecture.'''

import ipfshttpclient
import jwt
import logging
import socket
import uuid

from goldmine import Goldmine
from ident import Ident
from ipfshttpclient.multipart import BytesFileStream
from urlparse import urlparse


class MessageBus(Goldmine):

    APPLICATION_TYPE_MESSAGE_BUS = 'message_bus'
    CONNECTOR_TYPE_IPFS = 'ipfs'
    CONTRACT_METHOD_PUBLISH = 'publish'
    CONTRACT_TYPE_REGISTRY = 'registry'
    DEFAULT_MULTIPART_CHUNK_SIZE = 4096

    def __init__(self, token, wallet_address, multipart_chunk_size=DEFAULT_MULTIPART_CHUNK_SIZE):
        '''Initialize a message bus instance.'''
        super(MessageBus, self).__init__(token)
        self.ident = Ident(token)
        self.decode_jwt(token)
        self.wallet_address = wallet_address
        self.multipart_chunk_size = multipart_chunk_size
        self.resolve()
        self.init_ipfs()

    def init_ipfs(self):
        '''Initialize an IPFS client session.'''
        self.ipfsclient = None

        if self.connector == None:
            raise Exception('unable to establish IPFS client connection without resolution of a distributed filesystem connector')

        connector_addr = self.resolve_connector_multiaddr()
        if connector_addr == None:
            raise Exception('unable to establish IPFS client connection without resolution of configured distributed filesystem connector')

        self.ipfsclient = ipfshttpclient.connect(addr=connector_addr,
                                                 chunk_size=self.multipart_chunk_size,
                                                 session=True)

    def close(self):
        '''Free resources and exit.'''
        if self.ipfsclient != None:
            self.ipfsclient.close()

    def decode_jwt(self, token):
        '''Decode the given JWT.'''
        token = jwt.decode(token, verify=False)
        subparts = token['sub'].split(':')
        self.application_id = subparts[len(subparts) - 1]
        logging.info('resolved application id from JWT subject: {}'.format(self.application_id))

    def ipfs_add(self, msg, **kwargs):
        '''Add the given file to IPFS.'''
        if self.ipfsclient == None:
            raise Exception('unable to add file to IPFS without resolution of configured connector')

        filename = kwargs.pop('filename', '{}.bytes'.format(uuid.uuid4()))
        kwargs.setdefault('opts', {}).update({
            'wrap-with-directory': kwargs.pop('wrap_with_directory', False),
        }, **kwargs)

        stream = BytesFileStream(msg, name=filename, chunk_size=self.multipart_chunk_size)
        body, headers = stream.body(), stream.headers()
        return self.ipfsclient._client.request('/add', decoder='json', data=body, headers=headers, **kwargs)

    def publish_message(self, subject, msg, **kwargs):
        '''Publish a message.'''
        if self.contract == None:
            raise Exception('unable to publish message without resolution of an on-chain registry contract')

        if self.ipfsclient == None:
            raise Exception('unable to publish message without resolution of configured connector')

        resp = self.ipfs_add(msg, **kwargs)
        msghash = resp[len(resp) - 1]['Hash']
        logging.info('published {}-byte raw message to IPFS; hash: {}'.format(len(msg), msghash))

        status, _, _ = self.execute_contract(self.contract.get('id'), {
            'method': MessageBus.CONTRACT_METHOD_PUBLISH,
            'params': [subject, msghash],
            'value': 0,
            'wallet_address': self.wallet_address,
        })
        if status == 202:
            logging.info('published message on subject: {}'.format(subject))
        else:
            logging.warning('failed to publish message on subject: {}'.format(subject))

    def resolve(self):
        '''Resolve the application, on-chain registry contract and distributed filesystem connector.'''
        self.resolve_application()
        self.resolve_registry_contract()
        self.resolve_connector()

    def resolve_application(self):
        '''Resolve the message bus application.'''
        logging.info('resolving message bus application')
        self.application = None
        status, _, resp = self.ident.fetch_application_details(self.application_id)
        if status == 200:
            app_type = resp.get('config', {}).get('type', None)
            if app_type == MessageBus.APPLICATION_TYPE_MESSAGE_BUS:
                logging.info('resolved message bus application by id: {}'.format(self.application_id))
                self.application = resp
            else:
                logging.warning('failed to resolve message bus application by id: {}; application type: {}'.format(self.application_id, app_type))
        else:
            logging.warning('failed to resolve message bus application by id: {}'.format(self.application_id))

    def resolve_registry_contract(self):
        '''Resolve the on-chain registry contract for the message bus.'''
        logging.info('resolving on-chain registry contract for message bus')
        self.contract = None
        status, _, resp = self.fetch_contracts({
            'application_id': self.application_id,
        })
        if status == 200:
            for item in resp:
                _, _, contract = self.fetch_contract_details(item.get('id', None))
                contract_type = contract.get('params', {}).get('type', None)
                if contract_type == MessageBus.CONTRACT_TYPE_REGISTRY:
                    logging.info('resolved on-chain registry contract for application_id: {}; address: {}'.format(self.application_id, contract.get('address', None)))
                    self.contract = contract
                    break
                else:
                    logging.warning('failed to resolve on-chain registry contract for application_id: {}; contract type: {}'.format(self.application_id, contract_type))
        else:
            logging.warning('failed to resolve on-chain registry contract for application_id: {}'.format(self.application_id))

    def resolve_connector(self):
        '''Resolve the distributed filesystem connector for the message bus.'''
        logging.info('resolving distributed filesystem connector for message bus')
        self.connector = None
        status, _, resp = self.fetch_connectors({
            'application_id': self.application_id,
        })
        if status == 200:
            for item in resp:
                _, _, connector = self.fetch_connector_details(item.get('id', None))
                connector_type = connector.get('type', None)
                if connector_type == MessageBus.CONNECTOR_TYPE_IPFS:
                    logging.info('resolved distributed filesystem connector for application_id: {}; type: {}'.format(self.application_id, connector_type))
                    self.connector = connector
                    break
                else:
                    logging.warning('failed to resolve distributed filesystem connector for application_id: {}; connector type: {}'.format(self.application_id, connector_type))
        else:
            logging.warning('failed to resolve distributed filesystem connector for application_id: {}'.format(self.application_id))

    def resolve_connector_multiaddr(self):
        '''Resolve a distributed filesystem connector multiaddr for IPFS.'''
        api_url = self.connector.get('config', {}).get('api_url', None)
        if api_url == None:
            logging.warning('unable to resolve connector multiaddr without api_url')
            return None
        url = urlparse(api_url)
        ip = socket.gethostbyname(url.hostname)
        return '/ip4/{}/tcp/{}'.format(ip, url.port)
