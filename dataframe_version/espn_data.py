from typing import List, Tuple
from espn_api.basketball import League
from pandas.core.frame import DataFrame
from pandas.core.series import Series

import pandas as pd
import numpy as np
import json
import math

pd.options.mode.chained_assignment = None  # default='warn'

class EspnData:
    def __init__(self) -> None:
        self.league = League(
            league_id=1626888334,
            year=2022,
            espn_s2='AEB1q7wbcxFuEhtKHV%2Fw%2FpePdTBf1PPbePu8JV%2BpmXsSUHbLlWfEPioAA%2FA983DvVmc5NfcKYtKxBK4WZWCcoZdzoEeYjXLTVyA0TVbwsKG571X1YmCAS2urqwg8FO%2BONFDk%2BFSScnqPYqPwi9AS55zUJzMKxyxtLzNL2NlcbIBTAKwSVgPr3YTHqymKNF1fQNwmLiP%2Bv18BWa5jZxl8xO3WpgioNZKnTGisOXiXSXiWB%2B6Mb8B%2FvlL7Jz3fm7UZG026rdTXOvvFECyzyMrwu6I8',
            swid='{7FE52982-0E42-4123-A529-820E42E1232D}'
        )
        
        self.records_df = pd.DataFrame()
        self.zscores_df = pd.DataFrame()
        self.grades_df = pd.DataFrame()
        
        self.cats = ['PTS', 'BLK', 'STL', 'AST', 'REB', 'TO', 'FG%', 'FT%', '3PTM']
        self.season_years = ['2021', '2022']
        self.season_views = ['full', 'proj']
        self.stats_views = ['avg', 'total']

        self.data_dir = 'data/'
        self.records_json = self.data_dir + 'records.json'
        self.zscores_json = self.data_dir + 'zscores.json'
        self.grades_json = self.data_dir + 'grades.json'

    def run_api(self) -> None:
        self.get_player_records()
        self.calculate_grades()
        self.to_json()

    def from_json(self) -> Tuple[List, List, List]:
        with open(self.records_json, 'r') as f:
            records = json.load(f)
        with open(self.zscores_json, 'r') as f:
            zscores = json.load(f)
        with open(self.grades_json, 'r') as f:
            grades = json.load(f)
        return records, zscores, grades

    def to_json(self) -> None:
        self.records_df.to_json(self.records_json, orient='records')
        self.zscores_df.to_json(self.zscores_json, orient='records')
        self.grades_df.to_json(self.grades_json, orient='records')

    def zscore(self, df: DataFrame, col: str) -> Series:
        """Calculates zscore based on a DataFrame column."""
        return (df[col] - df[col].mean())/df[col].std(ddof=0)

    def zscore_percent(self, df: DataFrame, col: str) -> Series:
        """Calculates zscore for percent stats based on attempted."""
        # i.e. FG% -> FG -> FGA, FGM
        base = col[:-1]
        made, att = base + 'M', base + 'A'
        avg_p = df[made].sum()/df[att].sum()
        impact = (df[col] - avg_p)*df[att]

        # calculate zscores of impact
        df[col] = impact.values
        return self.zscore(df, col)
    
    def color(self, zscore) -> str:
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

        if math.isnan(zscore):
            return '#%02x%02x%02x' % white

        start, end = white, red if zscore < 0 else green

        x = abs(zscore)
        r, g, b = (int(x*end[i] + (1-x)*start[i]) for i in range(3))
        hex = '#%02x%02x%02x' % (clamp(r), clamp(g), clamp(b))
        return hex

    def calculate_grades(self) -> None:
        for season_year in self.season_years:
            for season_view in self.season_views:
                for stats_view in self.stats_views:
                    query = '`Season Year`=="{}" and `Season View`=="{}" and `Stats View`=="{}"'.format(season_year, season_view, stats_view)
                    query_df = self.records_df.query(query)
                    zscore_df = query_df.copy()
                    grade_df = query_df.copy()
                    numeric_cols = query_df.select_dtypes(include=[np.number])
                    
                    for col in numeric_cols:
                        zscore_df[col] = self.zscore_percent(query_df, col) if '%' in col else self.zscore(query_df, col)
                        grade_df[col] = zscore_df[col].map(lambda z: self.color(-z)) if col == 'TO' else zscore_df[col].map(lambda z: self.color(z))

                    # add zscores for each cat and calculate the zscore of the total
                    zscore_df['Z'] = zscore_df[self.cats].sum(axis=1, skipna=False)
                    zscore_df['Z'] = self.zscore(zscore_df, 'Z').round(2)
                    grade_df['Z'] = zscore_df['Z'].map(lambda z: self.color(z))
                    
                    rank = zscore_df['Z'].rank(ascending=False)
                    zscore_df.insert(4, 'R', rank)
                    grade_df.insert(4, 'R', rank)

                    self.zscores_df = zscore_df if self.zscores_df.empty else self.zscores_df.append(zscore_df)
                    self.grades_df = grade_df if self.grades_df.empty else self.grades_df.append(grade_df)
        
        self.zscores_df = self.zscores_df.sort_index()
        self.grades_df = self.grades_df.sort_index()
        self.records_df['Z'] = self.zscores_df['Z'].values
        self.records_df.insert(4, 'R', self.zscores_df['R'])

    def get_player_records(self) -> None:
        # XXYYYY: XX = full/proj, YYYY = year
        season_view_nums = {'full': '00', 'proj': '10'}
        stats = {'GP', 'MPG', 'PTS', 'AST', 'REB', 'STL', 'BLK', 'TO', 'FGM', 'FGA', 'FG%', 'FTM', 'FTA', 'FT%', '3PTM', '3PTA', '3PT%'}

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
                        season_view_num = season_view_nums[season_view]
                        season = season_view_num + season_year

                        for stats_view in self.stats_views:
                            player_stats = {}
                            try:
                                player_stats_data: dict = player_full_stats[season][stats_view]
                                for stat in stats:
                                    try:
                                        player_stats[stat] = round(player_stats_data[stat], 2)
                                    except KeyError:
                                        player_stats[stat] = 0.0
                            except KeyError:                                
                                for stat in stats:
                                    player_stats[stat] = None

                            player_record = {}
                            player_record['Fantasy Team'] = team_name
                            player_record['Season Year'] = season_year
                            player_record['Season View'] = season_view
                            player_record['Stats View'] = stats_view
                            player_record.update(player_info)
                            player_record.update(player_stats)
                            
                            self.records_df = self.records_df.append(player_record, ignore_index=True)
        
        col_order = ['Fantasy Team', 'Season Year', 'Season View', 'Stats View', 'Name', 'Pos', 'Team', 'GP', 'MPG', 'PTS', 'AST', 'REB', 'STL', 'BLK', 'TO', 'FGM', 'FGA', 'FG%', 'FTM', 'FTA', 'FT%', '3PTM', '3PTA', '3PT%']
        self.records_df = self.records_df[col_order]

if __name__ == "__main__":
    espnData = EspnData()
    espnData.run_api()