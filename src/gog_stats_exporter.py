#!/usr/bin/python3
import gog_extractor as gog
import steamprices_extractor as prices

import csv
import logging
import argparse
import time

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export stats from GOG Galaxy 2.0 to csv file.')
    parser.add_argument('-d', '--database', help='Path to GOG Galaxy 2.0 database.', default='galaxy-2.0.db')
    parser.add_argument('-o', '--output', help='Path to output csv file.', default='output.csv')
    parser.add_argument(
        '-p',
        '--proxied',
        help=
        'Using proxies to scrape websites faster. Use at your own risk! Without this setting the robots.txt is used to configure the delay between requests.',
        nargs='?',
        const=True,
        default=False)
    parser.add_argument(
        '--skip-prices',
        help=
        'Skips the annotations of price data from steamprices.com. Keep in mind that further analysis might not work because of the missing fields.',
        nargs='?',
        const=True,
        default=False)
    parser.add_argument('-l',
                        '--logging',
                        help='Defines log level.',
                        default='INFO',
                        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'])

    args = parser.parse_args()
    logging.basicConfig(level=args.logging, format='%(asctime)s %(levelname)-8s [%(name)s] %(message)s')
    logger = logging.getLogger('main')
    logger.debug('Provided command line args: %s', args)

    start = time.time()
    games = gog.extract(args)
    done = time.time()
    logger.debug('Elapsed time: %.2fs', done - start)

    if not args.skip_prices:
        start = time.time()
        games = prices.extract(args, games)
        done = time.time()
        logger.debug('Elapsed time: %.2fs', done - start)

    logger.info("Writing results to file...")
    headers = set()
    for value in games.values():
        headers.update(value.keys())
    headers = sorted(headers)

    with open(args.output, 'w', encoding='utf8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for game in games.values():
            writer.writerow(game)
    logger.info("Exporting finished!")
