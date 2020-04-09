#!/usr/bin/python3
import requests
import logging
import time
import multiprocessing
from bs4 import BeautifulSoup

logger = logging.getLogger('steamprices')
PROXY_LIST_URL = 'https://free-proxy-list.net/'
BASE_URL = 'https://www.steamprices.com/eu/'

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

    def process_task(self, proxy, queue, games):
        logger = logging.getLogger('proxy-' + proxy)
        try:
            google = requests.get("https://www.google.com", allow_redirects=False, proxies={"http": proxy, "https": proxy}, timeout=(5,15))
            if google.status_code != 200:
                raise Exception
        except:
            logger.debug('Dead proxy')
            return

        logger.debug('Using proxy')
        while not queue.empty():
            key = queue.get()
            try:
                result = requests.get(BASE_URL + 'app/' + games[key]['steamId'], allow_redirects=False, proxies={"http": proxy, "https": proxy}, timeout=(5, 30))
                if result.status_code not in [200, 404]:
                    raise requests.exceptions.ProxyError
                if result.status_code == 404:
                    result = requests.get(BASE_URL + 'dlc/' + games[key]['steamId'], allow_redirects=False, proxies={"http": proxy, "https": proxy}, timeout=(5, 30))
                    if result.status_code not in [200, 404]:
                        raise requests.exceptions.ProxyError
                    if result.status_code == 404:
                        raise AttributeError
                soup = BeautifulSoup(result.text, 'html.parser')
                text = soup.find('td', {'class': 'price_curent'}).span.text
                if text == 'Free':
                    games[key]['price.current'] = 0.0
                else:
                    games[key]['price.current'] = float(text.split(' ')[1])
                high = soup.find(text='Highest regular price:')
                if high == None:
                    games[key]['price.high'] = games[key]['price.current']
                else:
                    text = high.parent.parent.find('span', {'class': 'price'}).text
                    if text == 'Free':
                        games[key]['price.high'] = 0.0
                    else:
                        games[key]['price.high'] = float(text.split(' ')[1])
            except (requests.exceptions.ConnectTimeout, requests.exceptions.ProxyError):
                logger.debug('Proxy failed (timeout)')
                queue.put(key)
                return
            except (IndexError, AttributeError):
                logger.warning('Could not get price info of game "%s", Steam ID %s', games[key]['title.title'], games[key]['steamId'])
            except Exception as ex:
                logger.error('Unexpected exception: %s', ex)
                queue.put(key)
                return

    def extract(self):
        logger.info('Extracting prices from steamprices.com. This could take a while...')
        if not self.args.proxied:
            logger.critical('Non proxy mode not supported right now!')
            return self.games

        manager = multiprocessing.Manager()
        games = manager.dict()
        tasks = multiprocessing.Queue()
        for key in self.games.keys():
            games[key] = manager.dict()
            for k2 in self.games[key].keys():
                games[key][k2] = self.games[key][k2]
            if 'steamId' in self.games[key]:
                tasks.put(key)

        workers = []
        for proxy in self.get_proxies():
            worker = multiprocessing.Process(target=self.process_task, args=(proxy, tasks, games))
            workers.append(worker)
            worker.start()
        for worker in workers:
            worker.join()

        if not tasks.empty():
            logger.critical('Not all games annotated with price data. %d left. Probably ran out of proxies', tasks.qsize())

        result = dict()
        for key in games.keys():
            result[key] = dict()
            for k2 in games[key].keys():
                result[key][k2] = games[key][k2]
        return result