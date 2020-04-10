#!/usr/bin/python3
import gog_extractor as gog
import steamprices_extractor as prices

import csv
import logging
import argparse
import time

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export stats from GOG Galaxy 2.0 to csv file.')
    parser.add_argument('-d', '--database', help='path to GOG Galaxy 2.0 database', default ='galaxy-2.0.db')
    parser.add_argument('-o', '--output', help='path to output csv file', default ='output.csv')
    parser.add_argument('-p', '--proxied', help='using proxies to scrape websites faster', nargs='?', const=True, default =False)
    parser.add_argument('-l', '--logging', help='defines log level', default='INFO', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'])

    args = parser.parse_args()
    logging.basicConfig(level=args.logging,
                        format='%(asctime)s %(levelname)-8s [%(name)s] %(message)s')
    logger = logging.getLogger('main')
    logger.debug('Provided command line args: %s', args)

    start = time.time()
    games = gog.extract(args)
    done = time.time()
    logger.debug('Elapsed time: %f', done - start)

    start = time.time()
    games = prices.extract(args, games)
    done = time.time()
    logger.debug('Elapsed time: %f', done - start)

    headers = set()
    for value in games.values():
        headers.update(value.keys())
    headers = sorted(headers)

    with open(args.output, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for game in games.values():
            writer.writerow(game)