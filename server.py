import BaseHTTPServer
import predictit
import time
from urlparse import urlparse

HOST_NAME = '0.0.0.0'  # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 8000  # Maybe set this to 9000.


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(s):
        """Respond to a GET request."""
        query = urlparse(s.path).query
        query_components = dict(qc.split("=") for qc in query.split("&") if query != '')
        if urlparse(s.path).path == "/add":
            with open('markets.txt','a') as f:
                f.write(query_components['id'] + '\n')
            s.send_response(200)
            s.send_header("Content-type", "text/plain")
            s.end_headers()
            s.wfile.write("Ok, added " + query_components['id'] + "\n")
            return
        if urlparse(s.path).path == "/remove":
            with open('./markets.txt', 'r') as f:
                market_ids = set(f.read().strip().split('\n'))
            market_ids.discard(query_components['id'])
            with open('./markets.txt', 'w') as f:
                f.write('\n'.join(list(market_ids)) + '\n')
            s.send_response(200)
            s.send_header("Content-type", "text/plain")
            s.end_headers()
            s.wfile.write("Ok, removed " + query_components['id'] + "\n")
            return
        if urlparse(s.path).path != "/":
            s.send_response(404)
            s.end_headers()
            return
        s.send_response(200)
        s.send_header("Content-type", "text/plain")
        s.end_headers()
        s.wfile.write(predictit.get_data())

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
