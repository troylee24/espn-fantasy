from typing import List, Tuple
from espn_api.basketball import League
from collections import defaultdict
import json
import pandas as pd
from pandas.core.frame import DataFrame
from pandas.core.series import Series

"""LEAGUE SETTINGS"""
league_id = 1626888334
year = 2022
espn_s2 = 'AEB1q7wbcxFuEhtKHV%2Fw%2FpePdTBf1PPbePu8JV%2BpmXsSUHbLlWfEPioAA%2FA983DvVmc5NfcKYtKxBK4WZWCcoZdzoEeYjXLTVyA0TVbwsKG571X1YmCAS2urqwg8FO%2BONFDk%2BFSScnqPYqPwi9AS55zUJzMKxyxtLzNL2NlcbIBTAKwSVgPr3YTHqymKNF1fQNwmLiP%2Bv18BWa5jZxl8xO3WpgioNZKnTGisOXiXSXiWB%2B6Mb8B%2FvlL7Jz3fm7UZG026rdTXOvvFECyzyMrwu6I8'
swid = '{7FE52982-0E42-4123-A529-820E42E1232D}'
league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
# 0020XX is full season stats for 20XX (e.g. 002021)
# 1020XX is projected season stats for 20XX (e.g. 102021)
valid_seasons = {'002021', '102021', '002022', '102022'}
season_views = {'00': 'full', '10': 'proj'}

def zscore(df: DataFrame, col: str) -> Series:
    """Calculates zscore based on a DataFrame column."""
    return (df[col] - df[col].mean())/df[col].std(ddof=0)

def zscore_percent(df: DataFrame, col: str) -> Series:
    """Calculates zscore for percent stats based on attempted."""
    # i.e. FG% -> FG -> FGA, FGM
    base = col[:-1]
    made = base + 'M'
    att = base + 'A'
    avg_p = df[made].sum()/df[att].sum()
    impact = (df[col] - avg_p)*df[att]

    # calculate zscores of impact
    df[col] = impact
    return zscore(df, col)

def get_color(zscore) -> str:
    """
    Assigns a color based on a 3-point gradient of red-white-green
    Returns 6-digit hexadecimal string based on zscore.
    """
    def clamp(x):
        """Clamps rgb value to (0, 255)."""
        return max(0, min(x, 255))
    
    red = (255, 0, 0)
    white = (255, 255, 255)
    green = (0, 255, 0)
    if zscore < 0:
        start = white
        end = red
    else:
        start = white
        end = green
    x = abs(zscore)
    r, g, b = (int(x*end[i] + (1-x)*start[i]) for i in range(3))
    hex = '#%02x%02x%02x' % (clamp(r), clamp(g), clamp(b))
    return hex

def calculate_grades(data: dict) -> None:
    """
    Writes the zscores of each record to a json file.
    Writes the color grades of each record to a json file.
    """
    zscores_full_df = pd.DataFrame()
    grades_full_df = pd.DataFrame()

    for season_year in data:
        for season_view in data[season_year]:
            for stats_view in data[season_year][season_view]:
                records = data[season_year][season_view][stats_view]
                df = pd.DataFrame(records)
                zscore_df = pd.DataFrame(records)
                grade_df = pd.DataFrame(records)
                # calculate zscore for stat -> calculate color grade for zscore
                for col in df.columns:
                    if df[col].dtype == "float64":
                        if '%' in col:
                            zscore_df[col] = zscore_percent(df, col)
                        else:
                            zscore_df[col] = zscore(df, col)
                        if col == 'TO':
                            grade_df[col] = zscore_df[col].map(lambda z: get_color(-z))
                        else:
                            grade_df[col] = zscore_df[col].map(lambda z: get_color(z))
                
                # add total zscore column and calculate zscore for that column
                cats = ['PTS', 'BLK', 'STL', 'AST', 'REB', 'TO', 'FG%', 'FT%', '3PTM']
                zscore_df['Z'] = zscore_df[cats].sum(axis=1)
                zscore_df['Z'] = zscore(zscore_df, 'Z').round(2)
                grade_df['Z'] = zscore_df['Z'].map(lambda z: get_color(z))

                # add dataframes to resulting dataframe
                zscores_full_df = zscore_df if zscores_full_df.empty else zscores_full_df.append(zscore_df, ignore_index=True)
                grades_full_df = grade_df if grades_full_df.empty else grades_full_df.append(grade_df, ignore_index=True)

    # sort values by id in order to match the stats.json data
    zscores_full_df = zscores_full_df.sort_values(by=['id'])
    grades_full_df = grades_full_df.sort_values(by=['id'])

    # write dataframes to json
    zscores_full_df.to_json('data/zscores.json', orient="records")
    grades_full_df.to_json('data/grades.json', orient="records")

def data_to_json() -> None:
    """
    Root function that interprets ESPN fantasy basketball league data to be eventually passed to Flask app.
    In the end, should have indirectly/directly produced: grades.json, stats.json, zscores.json 
    """
    team_roster_stats = []
    grades_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    id = 0

    for team in league.teams:
        team_name = " ".join(team.team_name.split())

        for player in team.roster:
            # split player attributes into info (non-numeric) and stats (numeric)
            player_info: dict = vars(player)
            player_full_stats: dict = player_info['stats']
            # deleting unwanted attributes
            keys_to_delete = ['playerId', 'stats', 'injured', 'eligibleSlots', 'lineupSlot', 'acquisitionType', 'injuryStatus']
            for key in keys_to_delete:
                del player_info[key]
            # renaming keys
            keys_to_rename = {'name': 'Name', 'position': 'Pos', 'proTeam': 'Team'}
            for old, new in keys_to_rename.items():
                player_info[new] = player_info.pop(old)

            for season in player_full_stats:
                if not season in valid_seasons:
                    continue
                # i.e. 002022 -> 00 (view) + 2022 (year)
                season_year = season[2:]
                season_view = season_views[season[:2]]
                
                for stats_view in player_full_stats[season]:
                    # player stats for each season_year, season_view, and stats_view
                    player_stats: dict = player_full_stats[season][stats_view]
                    # filling in missing stats
                    stats_missing = ['3PTM', '3PTA', '3PT%']
                    for stat in stats_missing:
                        try:
                            player_stats[stat]
                        except KeyError:
                            player_stats[stat] = 0.0
                    # deleting unwanted stats
                    stats_to_delete = ['OREB', 'DREB', 'PF', 'GS', 'MIN']
                    for stat in stats_to_delete:
                        try:
                            del player_stats[stat]
                        except KeyError:
                            pass
                    # rounding floats to 2 decimals
                    for key, value in player_stats.items():
                        if isinstance(value, float):
                            player_stats[key] = round(value, 2)
                    
                    # build full player data
                    player_data = {}
                    player_data["id"] = id
                    player_data["Fantasy Team"] = team_name
                    player_data["Season Year"] = season_year
                    player_data["Season View"] = season_view
                    player_data["Stats View"] = stats_view
                    player_data.update(player_info)
                    player_data.update(player_stats)

                    # reorder dictionary so that it is consistent with grades.json and zscores.json
                    order = ['id', 'Fantasy Team', 'Season Year', 'Season View', 'Stats View', 'Name', 'Pos', 'Team', 'GP', 'MPG', 'PTS', 'BLK', 'STL', 'AST', 'REB', 'TO', 'FGM', 'FGA', 'FG%', 'FTM', 'FTA', 'FT%', '3PTM', '3PTA', '3PT%']
                    ordered_player_data = {}
                    for key in order:
                        ordered_player_data[key] = player_data[key]

                    # flask records
                    team_roster_stats.append(ordered_player_data)

                    # grades
                    grades_dict[season_year][season_view][stats_view].append(ordered_player_data)

                    id += 1
    
    # produce zscores.json and grades.json
    calculate_grades(grades_dict)

    # copy total z score key to every record
    with open('data/zscores.json', 'r') as f:
        zscores = json.load(f)

    for i in range(len(zscores)):
        team_roster_stats[i]['Z'] = zscores[i]['Z']
    
    with open('data/stats.json', 'w') as f:
        json.dump(team_roster_stats, f)

def json_to_data() -> Tuple[List, List]:
    """Returns loaded data from stats.json and grades.json to be passed to Flask app"""
    with open('data/stats.json', 'r') as f:
        data = json.load(f)
    with open('data/grades.json', 'r') as f:
        grades = json.load(f)
    return data, grades

if __name__ == "__main__":
    data_to_json()