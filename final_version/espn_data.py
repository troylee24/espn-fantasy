from typing import List
from espn_api.basketball import League
from collections import defaultdict
from season_table import SeasonTable

import pandas as pd
import json
import os

def get_data() -> tuple:
    data_dir = 'data'
    season_dirs = os.listdir(data_dir)
    n = len(season_dirs)
    names_tables = [str()] * n
    records_tables = [list()] * n
    zscores_tables = [list()] * n
    grades_tables = [list()] * n

    for i in range(n):
        season_dir = season_dirs[i]
        names_tables[i] = season_dir

        records_json = os.path.join(data_dir, season_dir, 'records.json')
        zscores_json = os.path.join(data_dir, season_dir, 'zscores.json')
        grades_json = os.path.join(data_dir, season_dir, 'grades.json')

        with open(records_json, 'r') as f:
            records_tables[i] = json.load(f)
        with open(zscores_json, 'r') as f:
            zscores_tables[i] = json.load(f)
        with open(grades_json, 'r') as f:
            grades_tables[i] = json.load(f)
    
    return names_tables, records_tables, zscores_tables, grades_tables

class EspnData:
    def __init__(self) -> None:
        self.league = League(
            league_id=1626888334,
            year=2022,
            espn_s2='AEB1q7wbcxFuEhtKHV%2Fw%2FpePdTBf1PPbePu8JV%2BpmXsSUHbLlWfEPioAA%2FA983DvVmc5NfcKYtKxBK4WZWCcoZdzoEeYjXLTVyA0TVbwsKG571X1YmCAS2urqwg8FO%2BONFDk%2BFSScnqPYqPwi9AS55zUJzMKxyxtLzNL2NlcbIBTAKwSVgPr3YTHqymKNF1fQNwmLiP%2Bv18BWa5jZxl8xO3WpgioNZKnTGisOXiXSXiWB%2B6Mb8B%2FvlL7Jz3fm7UZG026rdTXOvvFECyzyMrwu6I8',
            swid='{7FE52982-0E42-4123-A529-820E42E1232D}'
        )

        self.stats = ['GP', 'MPG', 'PTS', 'AST', 'REB', 'STL', 'BLK', 'TO', 'FGM', 'FGA', 'FG%', 'FTM', 'FTA', 'FT%', '3PTM', '3PTA', '3PT%']
        self.cats = ['PTS', 'BLK', 'STL', 'AST', 'REB', 'TO', 'FG%', 'FT%', '3PTM']

        # XXYYYY: XX = full/proj, YYYY = year
        self.season_years = ['2021', '2022']
        self.season_views = ['curr', 'proj']
        self.season_view_nums = {'curr': '00', 'proj': '10'} 
        self.stats_views = ['avg', 'total']

        self.season_tables: List[SeasonTable] = []

    def calculate_total_zscores(self, cats: List[str]) -> None:
        for season_table in self.season_tables:
            season_table.calculate_total_zscores(cats)
            season_table.to_json()

    def create_season_tables(self) -> None:
        self.season_tables = []
        records_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

        for team in self.league.teams:
            team_name = " ".join(team.team_name.split())
            
            for player in team.roster:
                player_vars: dict = vars(player)

                player_info = {}
                attributes = {'name': 'Name', 'position': 'Pos', 'proTeam': 'Team'}
                for old, new in attributes.items():
                    player_info[new] = player_vars[old]
                
                player_full_stats: dict = player_vars['stats']

                for season_year in self.season_years:
                    for season_view in self.season_views:
                        season_view_num = self.season_view_nums[season_view]
                        season = season_view_num + season_year

                        for stats_view in self.stats_views:
                            player_stats = {}
                            try:
                                player_stats_data: dict = player_full_stats[season][stats_view]
                                for stat in self.stats:
                                    try:
                                        player_stats[stat] = round(player_stats_data[stat], 2)
                                    except KeyError:
                                        player_stats[stat] = 0.0
                            except KeyError:                                
                                for stat in self.stats:
                                    player_stats[stat] = None

                            player_record = {}
                            player_record['Fantasy Team'] = team_name
                            player_record.update(player_info)
                            player_record.update(player_stats)
                            
                            records_dict[season_year][season_view][stats_view].append(player_record)
        
        for season_year in self.season_years:
            for season_view in self.season_views:
                for stats_view in self.stats_views:
                    records = records_dict[season_year][season_view][stats_view]
                    records_df = pd.DataFrame(records)
                    season_table = SeasonTable(season_year, season_view, stats_view, records_df, self.cats)
                    self.season_tables.append(season_table)

if __name__ == "__main__":
    espnData = EspnData()