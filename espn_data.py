from espn_api.basketball import League
from collections import defaultdict
import json
import pandas as pd
from pandas.core.frame import DataFrame

league_id = 1626888334
year = 2022
espn_s2 = 'AEB1q7wbcxFuEhtKHV%2Fw%2FpePdTBf1PPbePu8JV%2BpmXsSUHbLlWfEPioAA%2FA983DvVmc5NfcKYtKxBK4WZWCcoZdzoEeYjXLTVyA0TVbwsKG571X1YmCAS2urqwg8FO%2BONFDk%2BFSScnqPYqPwi9AS55zUJzMKxyxtLzNL2NlcbIBTAKwSVgPr3YTHqymKNF1fQNwmLiP%2Bv18BWa5jZxl8xO3WpgioNZKnTGisOXiXSXiWB%2B6Mb8B%2FvlL7Jz3fm7UZG026rdTXOvvFECyzyMrwu6I8'
swid = '{7FE52982-0E42-4123-A529-820E42E1232D}'
league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
# 0020XX is full season stats for 20XX (e.g. 002021)
# 1020XX is projected season stats for 20XX (e.g. 102021)
valid_seasons = {'002021', '102021', '002022', '102022'}
season_views = {'00': 'full', '10': 'proj'}

# regular zscore calculation
def zscore(df: DataFrame, col):
    return (df[col] - df[col].mean())/df[col].std(ddof=0)

# calculates zscore for percent stats based on attempted
def zscore_percent(df: DataFrame, col):
    # i.e. FG% -> FG -> FGA, FGM
    base = col[:-1]
    made = base + 'M'
    att = base + 'A'
    avg_p = df[made].sum()/df[att].sum()
    impact = (df[col] - avg_p)*df[att]

    # calculate zscores of impact
    df[col] = impact
    return zscore(df, col)

def get_color(zscore):
    def clamp(x):
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

def calculate_grades(data: dict):
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    for season_year in data:
        for season_view in data[season_year]:
            for stats_view in data[season_year][season_view]:
                records = data[season_year][season_view][stats_view]
                df = pd.DataFrame(records)
                zscore_df = pd.DataFrame(records)
                grade_df = pd.DataFrame(records)
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
                
                df1 = zscore_df if df1.empty else df1.append(zscore_df, ignore_index=True)
                df2 = grade_df if df2.empty else df2.append(grade_df, ignore_index=True)

    df1 = df1.sort_values(by=['id'])
    df2 = df2.sort_values(by=['id'])

    df1.to_json('data/zscores.json', orient="records")
    df2.to_json('data/grades.json', orient="records")

def data_to_json() -> None:
    team_roster_stats = []
    grades_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    id = 0

    for team in league.teams:
        team_name = " ".join(team.team_name.split())
        roster_stats = defaultdict(lambda: defaultdict(list))

        for player in team.roster:
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
                # 002022 -> 00 (view) + 2022 (year)
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

                    order = ['id', 'Fantasy Team', 'Season Year', 'Season View', 'Stats View', 'Name', 'Pos', 'Team', 'GP', 'MPG', 'PTS', 'BLK', 'STL', 'AST', 'REB', 'TO', 'FGM', 'FGA', 'FG%', 'FTM', 'FTA', 'FT%', '3PTM', '3PTA', '3PT%']
                    ordered_player_data = {}
                    for key in order:
                        ordered_player_data[key] = player_data[key]

                    # flask records
                    team_roster_stats.append(ordered_player_data)

                    # grades
                    grades_dict[season_year][season_view][stats_view].append(ordered_player_data)

                    id += 1
    
    with open("data/stats.json", 'w') as f:
        json.dump(team_roster_stats, f)
    
    calculate_grades(grades_dict)

def json_to_data():
    with open('data/stats.json', 'r') as f:
        data = json.load(f)
    with open('data/grades.json', 'r') as f:
        grades = json.load(f)
    return data, grades

if __name__ == "__main__":
    data_to_json()