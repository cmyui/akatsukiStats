# -*- coding: utf-8 -*-

from typing import Optional, Union, Dict, List, Tuple
import requests # You will need to install this with pip (i.e. `pip install requests`)
from time import time

from os.path import dirname, realpath, __file__
same_directory: str = dirname(realpath(__file__))

__version__: float = 1.04 # 2020-04-19

##############   Configuration
###############   > (Probably the only thing you need to touch)
################  > If you have any questions, contact cmyui#0425.
config = {
    'username_or_id': 1001, # the user's username *or* id (1001, or 'cmyui' ('' included))
    'gamemode': 'std', # the gamemode you want info for (std, taiko, ctb, mania)
    'relax': True, # do you want their relax profile? (True/False)

    'update_interval': 5, # how often to fetch updated stats (in seconds)

    'file_output': False, # enable to output to a file (for obs file reading)
    'file_path': f'{same_directory}/stats.txt' # output file, defaults to same directory as the script
                                               # does nothing unless file_output is True
}

# This is a list of what you want printed to the screen
# The options are: pp, rank, accuracy, ranked_score, total_score, level and playcount.
enabled = ['pp', 'rank', 'accuracy', 'ranked_score', 'total_score', 'level', 'playcount']

# String formats
# You can change these if you want to change the way the strings work.
# NOTE: I wouldn't mess with this unless you at least somewhat know what you're doing,
#       this needs perfect python format or will just spit errors everywhere.
# Example URL: https://akatsuki.pw/api/v1/users/rxfull?id=1001
# Vars: https://cdn.discordapp.com/attachments/686284366061764691/701316771457794078/unknown.png
strings = {
    'pp':           'PP:        {ranking_info["pp"]:,}',
    'rank':         'Rank:      #{ranking_info["global_leaderboard_rank"]} (#{ranking_info["country_leaderboard_rank"]} {json["country"]})',
    'accuracy':     'Accuracy:  {round(ranking_info["accuracy"], 2)}%', # i know :2f exists, but it doesn't seem to work here..
    'ranked_score': 'Score (R): {ranking_info["ranked_score"]:,}',
    'total_score':  'Score (T): {ranking_info["total_score"]:,}',
    'level':        'Level:     {round(ranking_info["level"], 2)}', # or here
    'playcount':    'Playcount: {ranking_info["playcount"]:,} ({formatPeriod(ranking_info["playtime"])})'
}

################# End of configuration
################
##############

def formatPeriod(seconds: int) -> str:
    days = int(seconds / 60 / 60 / 24)
    seconds %= (60 * 60 * 24)
    hours = int(seconds / 60 / 60)
    seconds %= (60 * 60)
    minutes = int(seconds / 60)
    return f'{days}d {hours}h {minutes}m'

def getStats(_config: Dict[str, Optional[Union[float, int, str]]], _options: List[str]) \
        -> Optional[Dict[str, Optional[Union[float, int, str]]]]:

    r = requests.get('https://akatsuki.pw/api/v1/users/{rx}full?{using_id}={name_or_id}'.format( # Send our API request off
        rx = 'rx' if _config['relax'] else '',
        using_id = 'id' if type(_config['username_or_id']) is int or _config['username_or_id'].isdigit() else 'name',
        name_or_id = _config['username_or_id']
    ))

    if not r or r.status_code != 200:
        return

    json: Dict[str, Optional[Union[float, int, str]]] = r.json()
    ranking_info: Dict[str, Optional[Union[float, int, str]]] = json[_config['gamemode']] # pylint: disable=unused-variable
    del r

    _p: List[str] = [] # can't be done in an iterator sadly
    for o in _options: _p.append(eval(f"f'{strings[o]}'"))
    return '\n'.join(_p)


from time import sleep
from os import system, name
if __name__ == '__main__':
    stats: Optional[str] = None

    while True:
        if not (stats := getStats(config, enabled)):
            print('Failed to get data from API.\nThe Akatsuki server may be down.')
            break

        system('cls' if name == 'nt' else 'clear')
        print(stats)

        if (config['file_output']):
            with open(config['file_path'], 'w+') as f:
                f.write(stats)

        sleep(config['update_interval'])
