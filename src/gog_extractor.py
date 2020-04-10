#!/usr/bin/python3
import os
import logging
import sqlite3
import json
import collections

logger = logging.getLogger('gog')
GAME_STMT = '''SELECT OwnedGames.releaseKey, GamePieceTypes.type, GamePieces.userId, GamePieces.value FROM OwnedGames
               LEFT JOIN GamePieces ON GamePieces.releaseKey = OwnedGames.releaseKey
               LEFT JOIN GamePieceTypes ON GamePieces.gamePieceTypeId = GamePieceTypes.id'''
ADDED_STMT = 'SELECT gameReleaseKey, userId, addedDate FROM ProductPurchaseDates WHERE userId <> 0'
TIME_STMT = 'SELECT releaseKey, minutesInGame, lastSessionEnd FROM GameTimes'

JOIN_KEYS = [
    'meta.developers', 'meta.genres', 'meta.publishers', 'meta.themes', 'myTags.tags',
    'originalMeta.developers', 'originalMeta.genres', 'originalMeta.publishers', 'originalMeta.themes'
]


def flatten(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def parseGames(results):
    games = dict()
    for id, type, userId, value in results:
        if id not in games:
            games[id] = dict()
        if type not in games[id] or (type in games[id] and userId):
            games[id][type] = json.loads(value)
    return games


def annotateInfo(games, key, col, results):
    for row in results:
        if row[0] in games:
            games[row[0]][key] = row[col]


def extract(args):
    logger.info('Extracting game list from GOG Galaxy 2.0...')
    if not os.path.isfile(args.database):
        raise Exception('Database does not exist: ' + args.database)

    conn = sqlite3.connect(args.database)
    c = conn.cursor()
    games = parseGames(c.execute(GAME_STMT))
    annotateInfo(games, 'addedDate', 2, c.execute(ADDED_STMT))
    annotateInfo(games, 'minutesInGame', 1, c.execute(TIME_STMT))
    annotateInfo(games, 'lastSessionEnd', 2, c.execute(TIME_STMT))
    conn.close()

    for key in games.keys():
        games[key] = flatten(games[key])
        for k in JOIN_KEYS:
            if k in games[key]:
                games[key][k] = ', '.join(games[key][k])
        for release in games[key]['allGameReleases.releases']:
            if release.startswith('steam_'):
                games[key]['steamId'] = release.replace('steam_', '')
                break
        games[key]['platform'] = key.split('_')[0].capitalize()

    return games
