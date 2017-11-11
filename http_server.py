from server import DBPool

from twisted.web import server, resource
from twisted.web.server import NOT_DONE_YET
from twisted.internet import reactor

import time
import json


class HTTPServer(resource.Resource):
    isLeaf = True
    def render(self, request):
        # print(dir(request))
        method = request.method.decode('utf-8')
        src_ip = request.getClientIP()
        host = request.getHeader('Host')
        path = request.path.decode('utf-8')
        parts = host.split('.')
        print(path, host, src_ip, method)
        
        if not host:
            # Requested by raw IP, we don't know what to do now
            print("No host header")
            return b"<html></html>"
        
        if parts[0] == 'export':
            return self.handle_export(request, path)
        elif len(parts) == 2: # domain
            return self.handle_index(path)
        else:
            # Log to database
            self.handle_subdomain(request)
            
                
        return b"<html>Hello, world!</html>"

    def handle_export(self, request, path):
        identifier = path[1:]
        def getHTTPRecords():
            return DBPool.runQuery("SELECT name, looked_up_at, ip, method, secure, type FROM query WHERE name LIKE ?", (identifier + '%',))
        
        def onResult(data):
            datadict = [{'name': d[0], 'looked_up_at': d[1], 'ip': d[2], 'method': d[3], 'secure': d[4], 'type': d[5]} for d in data]
            request.write(json.dumps(datadict).encode())
            request.finish()
        
        if len(identifier) >= 16 and '%' not in identifier and '_' not in identifier:
            d = getHTTPRecords()
            d.addCallback(onResult)
            return NOT_DONE_YET
        else:
            return b'<html>Nope</html>'
        
    def handle_index(self, path):
        return b'<html>Explanation</html>'

    def handle_subdomain(self, request):
        method = request.method.decode('utf-8')
        src_ip = request.getClientIP()
        host = request.getHeader('Host')
        path = request.path.decode('utf-8')
        isSecure = request.isSecure()
        reactor.callLater(1, self._insertIntoDB, 
                          method, host, src_ip, host, path, isSecure)
    
    def _insertIntoDB(self, method, name, src_ip, host, path, isSecure):
        timestamp = time.time()
        return DBPool.runInteraction(self._actualInsert, method, name, src_ip, host, path, isSecure, timestamp)
    
    def _actualInsert(self, tx, method, name, src_ip, host, path, isSecure, timestamp):
        tx.execute("INSERT INTO query(type, name, method, looked_up_at, ip, secure) VALUES ('HTTP',?,?,?,?,?)", (host,method,timestamp,src_ip,isSecure,))
    