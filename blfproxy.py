#!/usr/bin/env python

__verison__ = '0.1'
__license__ = 'MIT'

from ConfigParser import ConfigParser

from twisted.internet import ssl, defer
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.protocol import ReconnectingClientFactory


class Host(object):
    def __init__(self, address=None, port=None, user=None, secret=None,
                 use_ssl=False):
        '''Simple class for storing host information.'''
        self.address = address
        self.port = port
        self.user = user
        self.secret = secret
        self.use_ssl = use_ssl

class AMIClientProtocol(LineOnlyReceiver):
    def __init__(self):
        self._host = None
        self._user = None
        self._secret = None
        self._packet_cache = []
        self.ASTERISK_VERSION_STRING = 'Asterisk Call Manager'
        self.DEVICE_STATES = {'0': 'NOT_INUSE',
                              '1': 'INUSE',
                              '2': 'BUSY',
                              '4': 'UNAVAILABLE',
                              '8': 'RINGING',
                              '9': 'INUSE',
                              '16': 'ONHOLD'}
        
    def connectionMade(self):
        '''Adds the client to the list of connected clients in the factory and
        authenticates it.'''
        self.factory.clients.append(self)
        self._host = self.transport.getPeer().host
        self._user, self._secret = self.factory.get_credentials(self._host)
        self._authenticate()
        
    def lineReceived(self, line):
        '''Appends the incoming lines to the packet cache and calls the packet
        processing function when the packet is build.'''
        self._packet_cache.append(line)
        
        if not line.strip(): # end of packet (\r\n\r\n)
            self._handle_packet()
        
    def connectionLost(self, reason):
        '''Removes the client from the list of connected clients in the
        factory.'''
        self.factory.clients.remove(self)
        
    def _handle_packet(self):
        '''Handles the incoming AMI packet and clears the packet cache.'''
        packet = {}
        
        while self._packet_cache:
            line = self._packet_cache.pop(0).strip()
            
            if line and not line.startswith(self.ASTERISK_VERSION_STRING):
                line = line.split(':', 1)
                packet[line[0].lower().strip()] = line[1].lower().strip()
                
        self._process_packet(packet)
        
    def _process_packet(self, packet):
        '''Processes the incoming AMI packet.'''
        has_event = packet.get('event', False)
        
        if has_event and has_event == 'extensionstatus':
            new_packet = {'Action': 'Setvar',
                          'Variable': 'DEVICE_STATE(Custom:rhint_%s)' %
                          packet['exten'],
                          'Value': self.DEVICE_STATES[packet['status']]}
            
            self.factory.notify_others(self, new_packet)
            
    def _authenticate(self):
        '''Sends the login credentials to the AMI.'''
        self.send_packet({'Action': 'Login',
                          'Username': self._user,
                          'Secret': self._secret})
        
    def send_packet(self, packet):
        '''Sends a given packet to the AMI.'''
        for key, value in packet.iteritems():
            self.sendLine('%s: %s' % (key, value))
            
        self.sendLine('') # end of packet (\r\n\r\n)
        
class AMIClientFactory(ReconnectingClientFactory):
    protocol = AMIClientProtocol
    maxDelay = 300
    factor = 1.2
    
    def __init__(self, config):
        '''Reconnecting AMI client factory.'''
        self.clients = []
        self.hosts = self._get_hosts(config)

    def _get_hosts(self, config):
        '''Reads the configuration file and returns a list of hosts.'''
        hosts = []
        parser = ConfigParser()
        parser.read(config)
        
        for section in parser.sections():
            host = Host(parser.get(section, 'address'),
                        int(parser.get(section, 'port')),
                        section,
                        parser.get(section, 'secret'))
            
            if parser.get(section, 'usessl') == 'yes':
                host.use_ssl = True
            
            hosts.append(host)
            
        return hosts
        
    def notify_others(self, sender, packet):
        '''Sends a given packet to the other connected clients in the factory.
        '''
        for client in self.clients:
            if not client == sender:
                client.send_packet(packet)
    
    def get_credentials(self, address):
        '''Returns the login credentials for a given address (host).'''
        for host in self.hosts:
            if host.address == address:
                return host.user, host.secret
        
    def buildProtocol(self, address):
        '''Creates and instance of the client protocol and resets the
        connection delay.'''
        self.resetDelay()
        return ReconnectingClientFactory.buildProtocol(self, address)
        
    def clientConnectionLost(self, connector, reason):
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
    
    def clientConnectionFailed(self, connector, reason):
        ReconnectingClientFactory.clientConnectionFailed(self, connector,
                                                         reason)
        
if __name__ == '__main__':
    factory = AMIClientFactory('/etc/blfproxy/blfproxy.conf')
    from twisted.internet import reactor
    
    for host in factory.hosts:
        if (host.use_ssl):
            reactor.connectSSL(host.address, host.port, factory,
                               ssl.ClientContextFactory())
        else:
            reactor.connectTCP(host.address, host.port, factory)
    
    reactor.run()
else:
    from twisted.application.service import Application
    from twisted.application.internet import SSLClient, TCPClient
    from twisted.python.logfile import DailyLogFile
    from twisted.python.log import ILogObserver, FileLogObserver
    
    application = Application("BLFProxy")

    log_file = DailyLogFile("blfproxy.log", "/var/log")
    application.setComponent(ILogObserver, FileLogObserver(log_file).emit)
    
    factory = AMIClientFactory('/etc/blfproxy/blfproxy.conf')
    
    for host in factory.hosts:
        if (host.use_ssl):  
            service = SSLClient(host.address, host.port, factory,
                                ssl.ClientContextFactory())
            service.setServiceParent(application)
        else:
            service = TCPClient(host.address, host.port, factory)
            service.setServiceParent(application)
