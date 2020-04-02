#!/usr/bin/python3
import sqlite3
import csv
import json
import logging
import argparse
import helper
import os

parser = argparse.ArgumentParser(description='Export stats from GOG Galaxy 2.0 to csv file.')
parser.add_argument('-d', '--database', help='path to GOG Galaxy 2.0 database', default ='galaxy-2.0.db')
parser.add_argument('-o', '--output', help='path to output csv file', default ='output.csv')
parser.add_argument('-l', '--logging', help='defines log level', default='INFO', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'])

args = parser.parse_args()
logging.basicConfig(level=args.logging)

GAME_STMT = '''SELECT OwnedGames.releaseKey, GamePieceTypes.type, GamePieces.userId, GamePieces.value FROM OwnedGames
               LEFT JOIN GamePieces ON GamePieces.releaseKey = OwnedGames.releaseKey
               LEFT JOIN GamePieceTypes ON GamePieces.gamePieceTypeId = GamePieceTypes.id'''
ADDED_STMT = 'SELECT gameReleaseKey, userId, addedDate FROM ProductPurchaseDates WHERE userId <> 0'
TIME_STMT = 'SELECT releaseKey, minutesInGame, lastSessionEnd FROM GameTimes'

JOIN_KEYS = ['meta.developers', 'meta.genres', 'meta.publishers', 'meta.themes', 'myTags.tags', 'originalMeta.developers', 'originalMeta.genres', 'originalMeta.publishers', 'originalMeta.themes']

if not os.path.isfile(args.database):
    raise Exception('Database does not exist: ' + args.database)

conn = sqlite3.connect(args.database)
c = conn.cursor()
games = helper.parseGames(c.execute(GAME_STMT))
helper.annotateInfo(games, 'addedDate', 2, c.execute(ADDED_STMT))
helper.annotateInfo(games, 'minutesInGame', 1, c.execute(TIME_STMT))
helper.annotateInfo(games, 'lastSessionEnd', 2, c.execute(TIME_STMT))
conn.close()

headers = set()
for key in games.keys():
    games[key] = helper.flatten(games[key])
    for k in JOIN_KEYS:
        if k in games[key]:
            games[key][k] = ', '.join(games[key][k])
    for release in games[key]['allGameReleases.releases']:
        if release.startswith('steam_'):
            games[key]['steamId'] = release.replace('steam_', '')
            break
    games[key]['platform'] = key.split('_')[0]
    headers.update(games[key].keys())

headers = sorted(headers)

with open(args.output, 'w') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    for game in games.values():
        writer.writerow(game)