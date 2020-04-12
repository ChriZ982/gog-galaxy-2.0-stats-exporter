#!/usr/bin/python3
import requests
import logging
import time
import multiprocessing
from bs4 import BeautifulSoup

logger = logging.getLogger('steamprices')
PROXY_LIST_URL = 'https://free-proxy-list.net/'
BASE_URL = 'https://www.steamprices.com/eu/'
LOCAL = 'LOCAL'


def get_proxies():
    result = do_request(PROXY_LIST_URL, LOCAL)
    soup = BeautifulSoup(result.text, 'html.parser')
    table = soup.find('table', {'class': 'table'})
    return list(
        map(lambda row: row.contents[0].text + ':' + row.contents[1].text,
            list(table.findAll('tr'))[1:-1]))


def do_request(url, proxy):
    headers = {
        'User-Agent':
        'gog-galaxy-2.0-stats-exporter/0.2.1 https://github.com/ChriZ982/gog-galaxy-2.0-stats-exporter'
    }
    if proxy == LOCAL:
        return requests.get(url, allow_redirects=False, headers=headers)
    else:
        return requests.get(url,
                            allow_redirects=False,
                            proxies={
                                "http": proxy,
                                "https": proxy
                            },
                            headers=headers)


def process_task(proxy, queue, games):
    logger = logging.getLogger('worker-' + proxy)
    try:
        google = do_request("https://www.google.com", proxy)
        if google.status_code != 200:
            raise Exception
    except:
        logger.debug('Dead worker')
        return

    logger.debug('Started worker')
    while queue.qsize() > 0:
        try:
            key = queue.get_nowait()
            result = do_request(BASE_URL + 'app/' + games[key]['steamId'], proxy)
            if result.status_code not in [200, 404]:
                raise requests.exceptions.ProxyError
            if result.status_code == 404:
                result = do_request(BASE_URL + 'dlc/' + games[key]['steamId'], proxy)
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
            time.sleep(5)
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ProxyError,
                requests.exceptions.SSLError):
            logger.debug('Worker failed and was stopped')
            queue.put(key)
            return
        except (IndexError, AttributeError):
            logger.warning('Could not get price info of game "%s", Steam ID %s', games[key]['title.title'],
                           games[key]['steamId'])
        except Exception as ex:
            logger.error('Worker failed and was stopped. Unexpected cause: %s', ex)
            queue.put(key)
            return


def extract(args, games):
    logger.info('Extracting prices from steamprices.com.')
    if not args.proxied:
        logger.warning(
            "This will take 5 seconds per game (extimated duration for your game library: %ds). You can use --proxied argument at your own risk to speed it up or disable price data annotation by using --skip-prices.",
            5 * len(games.keys()))

    manager = multiprocessing.Manager()
    shared_games = manager.dict()
    tasks = multiprocessing.Queue()
    for key in games.keys():
        shared_games[key] = manager.dict()
        for k2 in games[key].keys():
            shared_games[key][k2] = games[key][k2]
        if 'steamId' in games[key]:
            tasks.put_nowait(key)
    size = tasks.qsize()
    previous = 0

    while tasks.qsize() > 0:
        workers = []
        proxies = [LOCAL]
        if args.proxied:
            proxies.extend(get_proxies())
        for proxy in proxies:
            worker = multiprocessing.Process(target=process_task, args=(proxy, tasks, shared_games))
            workers.append(worker)
            worker.start()
        for worker in workers:
            progress = 100 - tasks.qsize() / size * 100
            if progress > previous:
                logger.info('Progress: %.2f%%', progress)
                previous = progress
            worker.join()

    if tasks.qsize() > 0:
        logger.critical('Not all games annotated with price data. %d games left.', tasks.qsize())

    result = dict()
    for key in shared_games.keys():
        result[key] = dict()
        for k2 in shared_games[key].keys():
            result[key][k2] = shared_games[key][k2]
    return result
