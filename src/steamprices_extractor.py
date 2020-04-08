#!/usr/bin/python3
import requests
import logging
import time
from bs4 import BeautifulSoup

PROXY_LIST_URL = 'https://free-proxy-list.net/'
BASE_URL = 'https://www.steamprices.com/eu/app/'

class SteampricesExtractor:
    def __init__(self, args, games):
        self.args = args
        self.games = games
        self.proxies = []

    def get_proxies(self):
        result = requests.get(PROXY_LIST_URL)
        soup = BeautifulSoup(result.text, 'html.parser')
        table = soup.find('table', {'class': 'table'})
        return list(map(lambda row: row.contents[0].text + ':' + row.contents[1].text, list(table.findAll('tr'))[1:-1]))

    def do_request(self, steamId):
        result = ""
        if self.args.proxied:
            if len(self.proxies) == 0:
                logging.error('No proxies left. Starting over...')
                self.proxies = self.get_proxies()
            old_proxies = self.proxies.copy()
            for proxy in old_proxies:
                try:
                    logging.debug('Using proxy %s', proxy)
                    result = requests.get(BASE_URL + steamId, allow_redirects=False, proxies={"http": proxy, "https": proxy}, timeout=(1.5, 10))
                    if result.status_code in [200, 404]:
                        break
                    else:
                        self.proxies.remove(proxy)
                except Exception as ex:
                    self.proxies.remove(proxy)
                    logging.debug('Proxy %s not reachable: %s', proxy, ex)
        else:
            result = requests.get(BASE_URL + steamId, allow_redirects=False)
        return result

    def extract(self):
        logging.info('Extracting prices from steamprices.com. This could take a while...')

        if self.args.proxied:
            self.proxies = self.get_proxies()
        
        request_count = 0
        for key in self.games.keys():
            if 'steamId' not in self.games[key]:
                logging.info('Game "%s" has no Steam ID', self.games[key]['title.title'])
                continue
            try:
                result = self.do_request(self.games[key]['steamId'])
                if result.status_code == 302:
                    logging.error('Too many requests after %s were successful', request_count)
                    break
                if result.status_code != 200:
                    logging.warning('Could not get price info of game "%s", Steam ID %s', self.games[key]['title.title'], self.games[key]['steamId'])
                    continue
                request_count += 1
                soup = BeautifulSoup(result.text, 'html.parser')
                self.games[key]['price.current'] = float(soup.find('td', {'class': 'price_curent'}).span.text.split(' ')[1])
                self.games[key]['price.high'] = float(soup.find(text='Highest regular price:').parent.parent.find('span', {'class': 'price'}).text.split(' ')[1])
            except Exception as ex:
                logging.warning('Could not get price info of game "%s", Steam ID %s: %s', self.games[key]['title.title'], self.games[key]['steamId'], ex)
            if not self.args.proxied:
                time.sleep(5)
        return self.games