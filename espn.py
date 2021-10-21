from collections import defaultdict
import sqlite3
from espn_api.basketball import League
import pandas as pd
import json

league_id = 1626888334
year = 2022
espn_s2 = 'AEB1q7wbcxFuEhtKHV%2Fw%2FpePdTBf1PPbePu8JV%2BpmXsSUHbLlWfEPioAA%2FA983DvVmc5NfcKYtKxBK4WZWCcoZdzoEeYjXLTVyA0TVbwsKG571X1YmCAS2urqwg8FO%2BONFDk%2BFSScnqPYqPwi9AS55zUJzMKxyxtLzNL2NlcbIBTAKwSVgPr3YTHqymKNF1fQNwmLiP%2Bv18BWa5jZxl8xO3WpgioNZKnTGisOXiXSXiWB%2B6Mb8B%2FvlL7Jz3fm7UZG026rdTXOvvFECyzyMrwu6I8'
swid = '{7FE52982-0E42-4123-A529-820E42E1232D}'
league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
# 0020XX is full season stats for 20XX (e.g. 002021)
# 1020XX is projected season stats for 20XX (e.g. 102021)
valid_seasons = {'002021', '102021', '002022', '102022'}
season_types = {'00': 'full', '10': 'proj'}

def data_to_df(json_out=False):
    team_stats = []
    filters = defaultdict(set)

    for team in league.teams:
        team_name = " ".join(team.team_name.split())
        for player in team.roster:
            # filter out player data in dict copy
            player_dict = vars(player)
            player_dict_copy = player_dict.copy()
            keys_to_delete = ['playerId', 'stats', 'injured', 'eligibleSlots', 'lineupSlot', 'acquisitionType']
            for key in keys_to_delete:
                del player_dict_copy[key]

            # change dict to 1:1 relationship
            for season_type in player_dict['stats']:
                if not season_type in valid_seasons:
                    continue
                for stats_type in player_dict['stats'][season_type]:
                    player_data = {}
                    player_data["id"] = len(team_stats)

                    # team and stat options
                    player_data["fantasy_team"] = team_name
                    player_data["season"] = season_type[2:]
                    player_data["season_type"] = season_types[season_type[:2]]
                    player_data["stats_type"] = stats_type
                    filters["fantasy_team"].add(player_data["fantasy_team"])
                    filters["season"].add(player_data["season"])
                    filters["season_type"].add(player_data["season_type"])
                    filters["stats_type"].add(player_data["stats_type"])
                    
                    # add player non-stat attributes
                    player_data.update(player_dict_copy)
                    
                    # add player stat attributes
                    player_stats = player_dict['stats'][season_type][stats_type]
                    stat_conversions = {'3PTM': 'TPTM', '3PTA': 'TPTA', '3PT%': 'TPTP', 'FG%': 'FGP', 'FT%': 'FTP'}
                    for old, new in stat_conversions.items():
                        try:
                            player_stats[new] = player_stats.pop(old)
                        except KeyError:
                            player_stats[new] = 0.0
                    stats_to_delete = ['OREB', 'DREB', 'PF', 'GS']
                    for stat in stats_to_delete:
                        try:
                            del player_stats[stat]
                        except KeyError:
                            pass
                    player_data.update(player_stats)

                    # append to list of dictionaries
                    team_stats.append(player_data)

    filters = { key: sorted(list(value)) for key, value in filters.items() }
    with open('data/filters.json', 'w') as f:
        json.dump(filters, f)

    if json_out:
        with open('data/backup.json', 'w') as f:
            json.dump(team_stats, f)

    df = pd.DataFrame(team_stats)
    return df

def get_filters():
    with open('data/filters.json', 'r') as f:
        filters = json.load(f)
    return filters

if __name__ == "__main__":
    con = sqlite3.connect('data/stats.db')
    df = data_to_df(json_out=True)
    df.to_sql('stats', con=con, if_exists="replace")