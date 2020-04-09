#!/usr/bin/python3
import helper

import os
import logging
import sqlite3
import json

logger = logging.getLogger('gog')
GAME_STMT = '''SELECT OwnedGames.releaseKey, GamePieceTypes.type, GamePieces.userId, GamePieces.value FROM OwnedGames
               LEFT JOIN GamePieces ON GamePieces.releaseKey = OwnedGames.releaseKey
               LEFT JOIN GamePieceTypes ON GamePieces.gamePieceTypeId = GamePieceTypes.id'''
ADDED_STMT = 'SELECT gameReleaseKey, userId, addedDate FROM ProductPurchaseDates WHERE userId <> 0'
TIME_STMT = 'SELECT releaseKey, minutesInGame, lastSessionEnd FROM GameTimes'

JOIN_KEYS = ['meta.developers', 'meta.genres', 'meta.publishers', 'meta.themes', 'myTags.tags', 'originalMeta.developers', 'originalMeta.genres', 'originalMeta.publishers', 'originalMeta.themes']

def extract(args):
    logger.info('Extracting game list from GOG Galaxy 2.0...')
    if not os.path.isfile(args.database):
        raise Exception('Database does not exist: ' + args.database)

    conn = sqlite3.connect(args.database)
    c = conn.cursor()
    games = helper.parseGames(c.execute(GAME_STMT))
    helper.annotateInfo(games, 'addedDate', 2, c.execute(ADDED_STMT))
    helper.annotateInfo(games, 'minutesInGame', 1, c.execute(TIME_STMT))
    helper.annotateInfo(games, 'lastSessionEnd', 2, c.execute(TIME_STMT))
    conn.close()

    for key in games.keys():
        games[key] = helper.flatten(games[key])
        for k in JOIN_KEYS:
            if k in games[key]:
                games[key][k] = ', '.join(games[key][k])
        for release in games[key]['allGameReleases.releases']:
            if release.startswith('steam_'):
                games[key]['steamId'] = release.replace('steam_', '')
                break
        games[key]['platform'] = key.split('_')[0].capitalize()

    return games