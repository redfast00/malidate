#!/usr/bin/env python3

from twisted.internet import reactor, defer, protocol, ssl
from twisted.names import client, dns, error, server

import twisted.web
from twisted.enterprise import adbapi
from pprint import pprint
import time

import config, dns_server, http_server

DBPool = adbapi.ConnectionPool("sqlite3", config.db_file, check_same_thread=False)

class DNSServerFactory(server.DNSServerFactory):
    def __init__(self, DBPool, *args, **kwargs):
        self.DBPool = DBPool
        super().__init__(*args, **kwargs)

    def handleQuery(self, message, protocol, address):
        query = message.queries[0]
        src_ip = address[0]
        name = query.name.name.decode('utf-8')
        print('query=%r,src_ip=%r' % (name, src_ip))
        # TODO: only log actual requests
        reactor.callLater(1, self._insertIntoDB, name, src_ip)
        return self.resolver.query(query, src_ip).addCallback(
            self.gotResolverResponse, protocol, message, address
        ).addErrback(
            self.gotResolverError, protocol, message, address
        )
    
    def _insertIntoDB(self, name, src_ip):
        now = time.time()
        return self.DBPool.runInteraction(self._actualInsert, name, now, src_ip)

    def _actualInsert(self, tx, name, timestamp, src_ip):
        tx.execute("INSERT INTO query(type, name, looked_up_at, ip) VALUES ('DNS', ?,?,?)", (name,timestamp,src_ip,))

def main():
    '''Run the server.'''
    factory = DNSServerFactory(
        DBPool,
        clients=[dns_server.DynamicResolver(), client.Resolver(resolv='/etc/resolv.conf')]
    )
    # DNS Server
    protocol = dns.DNSDatagramProtocol(controller=factory)
    reactor.listenUDP(config.DNS_PORT, protocol)
    reactor.listenTCP(config.DNS_PORT, factory)
    # HTTP and HTTPS
    reactor.listenTCP(config.HTTP_PORT, twisted.web.server.Site(http_server.HTTPServer()))
    
    sslContext = ssl.DefaultOpenSSLContextFactory(
        config.HTTPS_KEY,  # Private Key
        config.HTTPS_CERT,  # Certificate
    )
    reactor.listenSSL(config.HTTPS_PORT, twisted.web.server.Site(http_server.HTTPServer()), sslContext)
    reactor.run()


if __name__ == '__main__':
    raise SystemExit(main())
