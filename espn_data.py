"""
This script writes data from an ESPN league to multiple json files.
Each file is created for a team's player's stats for a specific season, season_type(full/proj), and stat_type.
(i.e. if there were 2 seasons, 2 season_types, and 2 stat_types, a single player would have 6 different json files)
"""

from espn_api.basketball import League
from collections import defaultdict
import json
import os

league_id = 1626888334
year = 2022
espn_s2 = 'AEB1q7wbcxFuEhtKHV%2Fw%2FpePdTBf1PPbePu8JV%2BpmXsSUHbLlWfEPioAA%2FA983DvVmc5NfcKYtKxBK4WZWCcoZdzoEeYjXLTVyA0TVbwsKG571X1YmCAS2urqwg8FO%2BONFDk%2BFSScnqPYqPwi9AS55zUJzMKxyxtLzNL2NlcbIBTAKwSVgPr3YTHqymKNF1fQNwmLiP%2Bv18BWa5jZxl8xO3WpgioNZKnTGisOXiXSXiWB%2B6Mb8B%2FvlL7Jz3fm7UZG026rdTXOvvFECyzyMrwu6I8'
swid = '{7FE52982-0E42-4123-A529-820E42E1232D}'
league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
# 0020XX is full season stats for 20XX (e.g. 002021)
# 1020XX is projected season stats for 20XX (e.g. 102021)
valid_seasons = {'002021', '102021', '002022', '102022'}
season_types = {'00': 'full', '10': 'proj'}

def data_to_json():
    team_roster_stats = []
    for team in league.teams:
        roster_stats = defaultdict(lambda: defaultdict(list))
        for player in team.roster:
            # convert object to dict and filter wanted variables
            player_dict = vars(player)
            player_dict_copy = player_dict.copy()
            keys_to_delete = ['playerId', 'stats', 'injured', 'eligibleSlots', 'lineupSlot', 'acquisitionType']
            for key in keys_to_delete:
                del player_dict_copy[key]
            keys_to_rename = {'name': 'Name', 'position': 'Pos', 'proTeam': 'Team', 'injuryStatus': 'Status'}
            for old, new in keys_to_rename.items():
                player_dict_copy[new] = player_dict_copy.pop(old)
            # 8 dictionaries (same keys) = full/proj(2) * season(2) * avg/total(2)
            for season_type in player_dict['stats']:
                if not season_type in valid_seasons:
                    continue
                for stats_type in player_dict['stats'][season_type]:
                    player_stats = player_dict['stats'][season_type][stats_type]
                    stats_missing = ['3PTM', '3PTA', '3PT%']
                    for stat in stats_missing:
                        try:
                            player_stats[stat]
                        except KeyError:
                            player_stats[stat] = 0.0
                    stats_to_delete = ['OREB', 'DREB', 'PF', 'GS']
                    for stat in stats_to_delete:
                        try:
                            del player_stats[stat]
                        except KeyError:
                            pass
                    for key, value in player_stats.items():
                        if isinstance(value, float):
                            player_stats[key] = round(value, 2)
                    player_dict_copy.update(player_stats)
                    roster_stats[season_type][stats_type].append(player_dict_copy.copy())
        team_name = " ".join(team.team_name.split())
        for season_type in roster_stats:
            for stats_type in roster_stats[season_type]:
                modified_roster_stats = {}
                modified_roster_stats["fantasy_team"] = team_name
                modified_roster_stats["season"] = season_type[2:]
                modified_roster_stats["season_type"] = season_types[season_type[:2]]
                modified_roster_stats["stats_type"] = stats_type
                modified_roster_stats["stats"] = roster_stats[season_type][stats_type]
                team_roster_stats.append(modified_roster_stats)
    
    with open("data/stats.json", 'w') as f:
        json.dump(team_roster_stats, f)

def json_to_data():
    with open('data/stats.json', 'r') as f:
        data = json.load(f)
    return data

if __name__ == "__main__":
    data_to_json()