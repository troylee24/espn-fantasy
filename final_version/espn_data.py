from typing import List, Tuple
from espn_api.basketball import League, Team, Player
from collections import defaultdict
from season_table import SeasonTable
from team_table import TeamTable

import pandas as pd

class EspnData:
    def __init__(self) -> None:
        self.league = League(
            league_id=1626888334,
            year=2022,
            espn_s2='AEB1q7wbcxFuEhtKHV%2Fw%2FpePdTBf1PPbePu8JV%2BpmXsSUHbLlWfEPioAA%2FA983DvVmc5NfcKYtKxBK4WZWCcoZdzoEeYjXLTVyA0TVbwsKG571X1YmCAS2urqwg8FO%2BONFDk%2BFSScnqPYqPwi9AS55zUJzMKxyxtLzNL2NlcbIBTAKwSVgPr3YTHqymKNF1fQNwmLiP%2Bv18BWa5jZxl8xO3WpgioNZKnTGisOXiXSXiWB%2B6Mb8B%2FvlL7Jz3fm7UZG026rdTXOvvFECyzyMrwu6I8',
            swid='{7FE52982-0E42-4123-A529-820E42E1232D}'
        )

        self.cats = ['PTS', 'AST', 'REB', 'STL', 'BLK', 'TO', 'FG%', 'FT%', '3PTM']

        # XXYYYY: XX = full/proj, YYYY = year
        self.season_years = ['2021', '2022']
        self.season_views = ['curr', 'proj']
        self.season_view_nums = {'curr': '00', 'proj': '10'} 
        self.stats_views = ['avg', 'total']

        self.team_table: TeamTable = None
        self.season_tables: dict[str, SeasonTable] = {}

        self.create_season_tables()

    def get_season_table_headers(self) -> List[str]:
        return list(self.season_tables.values())[0].get_headers()

    def get_team_table_headers(self) -> Tuple[List[str], List[str]]:
        return self.team_table.get_headers()

    def get_season_ids(self):
        return self.season_tables.keys()

    def calculate_total_zscores(self, season_id: str, cats: List[str]) -> None:
        self.season_tables[season_id].calculate_total_zscores(cats)
        self.season_tables[season_id].to_json()

    def create_season_tables(self) -> None:
        team_list = []
        records_dict = defaultdict(list)

        team: Team = None
        for team in self.league.teams:
            team_name = " ".join(team.team_name.split())
            team_dict = {}
            team_dict['Fantasy Team'] = team_name
            for cat in self.cats:
                team_dict[cat] = round(team.stats[cat], 2)
            team_list.append(team_dict)
            
            player: Player = None
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
                            stats = ['GP', 'MPG', 'PTS', 'AST', 'REB', 'STL', 'BLK', 'TO', 'FGM', 'FGA', 'FG%', 'FTM', 'FTA', 'FT%', '3PTM', '3PTA', '3PT%']
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
                            player_record.update(player_info)
                            player_record.update(player_stats)
                            
                            season_id = "_".join((season_year, season_view, stats_view))
                            records_dict[season_id].append(player_record)

        team_df = pd.DataFrame(team_list)
        self.team_table = TeamTable(team_df)

        for season_id, records in records_dict.items():
            records_df = pd.DataFrame(records)
            season_table = SeasonTable(season_id, records_df, self.cats)
            self.season_tables[season_id] = season_table

if __name__ == "__main__":
    espnData = EspnData()