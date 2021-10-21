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
valid_seasons = {'002021', '102021', '102022'}
season_types = {'00': 'full', '10': 'proj'}
data_dir = "data"

def data_to_json():
    team_roster_stats = {}
    for team in league.teams:
        roster_stats = defaultdict(lambda: defaultdict(list))
        for player in team.roster:
            # convert object to dict and filter wanted variables
            player_dict = vars(player)
            player_dict_copy = player_dict.copy()
            keys_to_delete = ['stats', 'injured', 'eligibleSlots', 'lineupSlot', 'acquisitionType']
            for key in keys_to_delete:
                del player_dict_copy[key]
            # 6 dictionaries (same keys) = full/proj(2) + season(2) + avg/total(2)
            for season_type in player_dict['stats']:
                if not season_type in valid_seasons:
                    continue
                for stats_type in player_dict['stats'][season_type]:
                    player_stats = player_dict['stats'][season_type][stats_type]
                    for key, value in player_stats.items():
                        player_dict_copy[key] = value
                    roster_stats[season_type][stats_type].append(player_dict_copy)
        
        team_name = " ".join(team.team_name.split())
        team_roster_stats["team"] = team_name
        for season_type in roster_stats:
            for stats_type in roster_stats[season_type]:
                team_roster_stats["season"] = season_type[2:]
                team_roster_stats["season_type"] = season_types[season_type[:2]]
                team_roster_stats["stats_type"] = stats_type
                team_roster_stats["stats"] = roster_stats[season_type][stats_type]
                team_data_file = "{}/{}_{}_{}.json".format(data_dir, team_name, season_type, stats_type)
                with open(team_data_file, 'w') as f:
                    json.dump(team_roster_stats, f)

def json_to_data():
    data = []
    options = defaultdict(set)
    team_data_files = os.listdir(data_dir)
    for team_data_file in team_data_files:
        file_path = "{}/{}".format(data_dir, team_data_file)
        with open(file_path, 'r') as f:
            team_roster_stats = json.load(f)
        data.append(team_roster_stats)
        for key in team_roster_stats:
            if key == "stats":
                continue
            options[key].add(team_roster_stats[key])
    for option in options:
        options[option] = list(options[option])
        options[option].sort()
    return data, options

if __name__ == "__main__":
    data_to_json()
    # json_to_data()