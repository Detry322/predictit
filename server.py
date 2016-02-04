import BaseHTTPServer
import predictit
import random
import time
import thread
import smtplib
import subprocess
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
        s.wfile.write(predictit.print_markets(predictit.get_markets()))


def send_mail(to_addrs, subject, message):
    process = subprocess.Popen(['mail','-s', subject] + to_addrs, stdin=subprocess.PIPE)
    process.communicate(message)
    process.stdin.close()
    print "Email sent"


def email_thing():
    YES_CUTOFF = 4
    NO_CUTOFF = 0
    print "Starting notifier...."
    while True:
        markets = predictit.get_markets()
        should_email = False
        for market in markets:
            edges = market.edges()
            if edges[0] > YES_CUTOFF or edges[1] > NO_CUTOFF:
                if market.id == "1234":
                    continue
                print "Arbitrage found."
                should_email = True
                break
        if should_email:
            send_mail(["jserrino@gmail.com", "fserrino@aol.com"], "Check Predictit", predictit.print_markets(markets))
        sleep_time = int((random.random()-0.5)*600+600)
        time.sleep(sleep_time)

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        thread.start_new_thread(email_thing, ())
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
