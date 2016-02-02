from bs4 import BeautifulSoup
import grequests
import time
import BaseHTTPServer

URL_BASE = "https://www.predictit.org/Home/GetContractListAjax?marketId="


class Market:
    def __init__(self):
        self.contestants = []
        self.name = ""

    def add_contestant(self, name, buy_yes, sell_yes):
        self.contestants.append((name, buy_yes, sell_yes))

    def edges(self):
        if len(self.contestants) == 0:
            return (100, 100)

        yes_total = sum(contestant[1] for contestant in self.contestants)
        no_total = sum(contestant[2] for contestant in self.contestants)
        return (90-yes_total, no_total - 110, yes_total, no_total)


def get_title(soup):
    return soup.find(class_='sharesHeader').text.strip()


def parse_market(response):
    market = Market()
    soup = BeautifulSoup(response.text, "html.parser")
    market.name = get_title(soup)
    for match in soup.find('table', id="contractListTable").find('tbody').find_all('tr'):
        name_match = match.find('h4')
        if name_match is None:
            continue
        name = name_match.text.strip()
        buy_str, sell_str = match.find_all('span', class_='sharesUp')
        if buy_str.text == "None":
            buy = 100
        else:
            buy = int(buy_str.text[:-1])
        if sell_str.text == "None":
            sell = 0
        else:
            sell = int(sell_str.text[:-1])
        market.add_contestant(name, buy, sell)
    return market


HOST_NAME = '0.0.0.0' # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 8000 # Maybe set this to 9000.


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(s):
        """Respond to a GET request."""
        if s.path != "/":
            s.send_response(404)
            s.end_headers()
            return
        s.send_response(200)
        s.send_header("Content-type", "text/plain")
        s.end_headers()
        market_ids = None
        with open('./markets.txt', 'r') as f:
            market_ids = f.read().strip().split('\n')

        responses = grequests.map([grequests.get(URL_BASE + market_id) for market_id in market_ids])

        markets = [parse_market(response) for response in responses if response.status_code == 200]

        s.wfile.write("        market name | bye | bne | byt | bnt |\n")
        for market in markets:
            s.wfile.write("{: >19s} | {: >3d} | {: >3d} | {: >3d} | {: >3d} |\n".format(market.name, *market.edges()))

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
