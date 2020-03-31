#!/usr/bin/python3

import sqlite3
import csv
import json
import logging
import argparse
import helper
import os.path

parser = argparse.ArgumentParser(description='Export stats from GOG Galaxy 2.0 to csv file.')
parser.add_argument('-d', '--database', help='path to GOG Galaxy 2.0 database', default ='galaxy-2.0.db')
parser.add_argument('-o', '--output', help='path to output csv file', default ='output.csv')
parser.add_argument('-l', '--logging', help='defines log level', default='INFO', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'])

args = parser.parse_args()
logging.basicConfig(level=args.logging)

SELECT_STMT = '''SELECT OwnedGames.releaseKey, GamePieceTypes.type, GamePieces.value FROM OwnedGames
                    LEFT JOIN GamePieces ON GamePieces.releaseKey = OwnedGames.releaseKey
                    LEFT JOIN GamePieceTypes ON GamePieces.gamePieceTypeId = GamePieceTypes.id
                    WHERE GamePieceTypes.id IN (2,3,9,11,1684)'''
JOIN_KEYS = ['meta.developers', 'meta.genres', 'meta.publishers', 'meta.themes', 'myTags.tags']

if not os.path.isfile(args.database):
    raise Exception('Database does not exist: ' + args.database)

conn = sqlite3.connect(args.database)
c = conn.cursor()

games = dict()
headers = set()

for id, type, value in c.execute(SELECT_STMT):
    if id not in games:
        games[id] = dict()

    jsonValue = json.loads(value)
    if type in games[id] and games[id][type] != jsonValue:
        lenCur = len(json.dumps(jsonValue))
        lenEx = len(json.dumps(games[id][type]))
        logging.debug('%s already existing on %s: longer entry will be used (current: %d, existing: %d)', type, id, lenCur, lenEx)
        if lenCur > lenEx:
            games[id][type] = jsonValue
    else:
        games[id][type] = jsonValue

conn.close()

for key in games.keys():
    games[key] = helper.flatten(games[key])
    for k in JOIN_KEYS:
        if k in games[key]:
            games[key][k] = ', '.join(games[key][k])
    headers.update(games[key].keys())

headers = sorted(headers)

with open(args.output, 'w') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    for game in games.values():
        writer.writerow(game)