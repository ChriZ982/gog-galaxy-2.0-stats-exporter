#!/usr/bin/python3
import collections
import json

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