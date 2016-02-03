from bs4 import BeautifulSoup
import grequests


URL_BASE = "https://www.predictit.org/Home/GetContractListAjax?marketId="


class Market:
    def __init__(self, market_id):
        self.contestants = []
        self.name = ""
        self.id = market_id

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
    try:
        market = Market(response.url[-4:])
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
    except ValueError:
        return None


def get_data():
    result = ""
    market_ids = None
    with open('./markets.txt', 'r') as f:
        market_ids = list(set(f.read().strip().split('\n')))

    responses = grequests.map([grequests.get(URL_BASE + market_id) for market_id in market_ids])

    markets = [parse_market(response) for response in responses if response.status_code == 200]

    result += ("        market name |   id | bye | bne | byt | bnt |\n")
    market_results = sorted([(market.name, market.id) + market.edges() for market in markets if market is not None], key=lambda x: -x[3])
    for market in market_results:
        result += ("{: >19s} | {: >4s} | {: >3d} | {: >3d} | {: >3d} | {: >3d} |\n".format(*market))
    return result


if __name__ == "__main__":
    print get_data()
