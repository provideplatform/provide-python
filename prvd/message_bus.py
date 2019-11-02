'''API client for the provide.services message bus microservice architecture.'''

import ipfshttpclient
import jwt
import logging
import socket

from goldmine import Goldmine
from ident import Ident
from urlparse import urlparse


class MessageBus(Goldmine):

    APPLICATION_TYPE_MESSAGE_BUS = 'message_bus'
    CONNECTOR_TYPE_IPFS = 'ipfs'
    CONTRACT_METHOD_PUBLISH = 'publish'
    CONTRACT_TYPE_REGISTRY = 'registry'

    def __init__(self, token, wallet_address):
        '''Initialize a message bus instance.'''
        super(MessageBus, self).__init__(token)
        self.ident = Ident(token)
        self.decode_jwt(token)
        self.wallet_address = wallet_address
        self.resolve()

    def decode_jwt(self, token):
        '''Decode the given JWT.'''
        token = jwt.decode(token, verify=False)
        subparts = token['sub'].split(':')
        self.application_id = subparts[len(subparts) - 1]
        logging.info('resolved application id from JWT subject: {}'.format(self.application_id))

    def publish_message(self, subject, msg):
        '''Publish a message.'''
        if self.contract == None:
            raise Exception('unable to publish message without resolution of an on-chain registry contract')

        if self.connector == None:
            raise Exception('unable to publish message without resolution of a distributed filesystem connector')

        connector_addr = self.resolve_connector_multiaddr()
        if connector_addr == None:
            raise Exception('unable to publish message without resolution of configured connector multiaddr')

        msghash = None
        with ipfshttpclient.connect(addr=connector_addr) as ipfsclient:
            msghash = ipfsclient.add_bytes(msg)
            logging.info('published raw message to IPFS; hash: {}'.format(msghash))

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
