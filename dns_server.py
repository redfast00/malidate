from twisted.names import dns
from twisted.internet import defer
import config

class DynamicResolver(object):
    """
    A resolver which calculates the answers to certain queries based on the
    query type and name.
    """

    def _do_NS_response(self, name=None):
        answer = dns.RRHeader(
            name=name,
            payload=dns.Record_NS(ttl=10, name='ns1.'+name),
            type=dns.NS)
        additional = dns.RRHeader(
            name='ns1.'+name,
            payload=dns.Record_A(ttl=10, address=config.PUBLIC_IP),
            type=dns.A)
        answers = [answer]
        authority = []
        additional = [additional]
        return answers, authority, additional

    def _do_A_response(self, name=None):
        payload = dns.Record_A(ttl=10, address=config.PUBLIC_IP)
        answer = dns.RRHeader(
            name=name,
            payload=payload,
            type=dns.A)
        answers = [answer]
        authority = []
        additional = []
        return answers, authority, additional

    def _do_no_response(self):
        """
        Calculate the response to a query.
        """
        answers = []
        authority = []
        additional = []
        return answers, authority, additional

    def query(self, query, timeout=None):
        """
        Check if the query should be answered dynamically, otherwise dispatch to
        the fallback resolver.
        """
        if query.type == dns.A:
            return defer.succeed(self._do_A_response(query.name.name))
        elif query.type == dns.NS:
            return defer.succeed(self._do_NS_response(query.name.name))
        else:
            return defer.fail(error.DomainError())