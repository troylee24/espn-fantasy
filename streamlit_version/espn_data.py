from espn_api.basketball import League

import pandas as pd

pd.options.mode.chained_assignment = None  # default='warn'

class EspnData:
    def __init__(self) -> None:
        self.league = League(
            league_id=1626888334,
            year=2022,
            espn_s2='AEB1q7wbcxFuEhtKHV%2Fw%2FpePdTBf1PPbePu8JV%2BpmXsSUHbLlWfEPioAA%2FA983DvVmc5NfcKYtKxBK4WZWCcoZdzoEeYjXLTVyA0TVbwsKG571X1YmCAS2urqwg8FO%2BONFDk%2BFSScnqPYqPwi9AS55zUJzMKxyxtLzNL2NlcbIBTAKwSVgPr3YTHqymKNF1fQNwmLiP%2Bv18BWa5jZxl8xO3WpgioNZKnTGisOXiXSXiWB%2B6Mb8B%2FvlL7Jz3fm7UZG026rdTXOvvFECyzyMrwu6I8',
            swid='{7FE52982-0E42-4123-A529-820E42E1232D}'
        )
        self.season_years = ['2021', '2022']
        self.season_views = ['full', 'proj']
        self.stats_views = ['avg', 'total']
        
        self.records_df = pd.DataFrame()

    def get_player_records(self) -> None:
        # XXYYYY: XX = full/proj, YYYY = year
        valid_seasons = {'002021', '102021', '002022', '102022'}
        season_views = {'00': 'full', '10': 'proj'}

        for team in self.league.teams:
            team_name = " ".join(team.team_name.split())
            
            for player in team.roster:
                player_attr: dict = vars(player)
                player_full_stats: dict = player_attr['stats']

                # deleting unwanted attributes
                keys_to_delete = ['playerId', 'stats', 'injured', 'eligibleSlots', 'lineupSlot', 'acquisitionType', 'injuryStatus']
                for key in keys_to_delete:
                    del player_attr[key]
                # renaming keys
                keys_to_rename = {'name': 'Name', 'position': 'Pos', 'proTeam': 'Team'}
                for old, new in keys_to_rename.items():
                    player_attr[new] = player_attr.pop(old)
                
                player_info = player_attr

                for season in player_full_stats:
                    if not season in valid_seasons:
                        continue
                    season_year = season[2:]
                    season_view = season_views[season[:2]]

                    for stats_view in player_full_stats[season]:
                        player_stats: dict = player_full_stats[season][stats_view]
                        
                        stats_missing = ['3PTM', '3PTA', '3PT%']
                        for stat in stats_missing:
                            try: player_stats[stat]
                            except KeyError: player_stats[stat] = 0.0

                        stats_to_delete = ['OREB', 'DREB', 'PF', 'GS', 'MIN']
                        for stat in stats_to_delete:
                            try: del player_stats[stat]
                            except KeyError: pass
                        
                        for key, value in player_stats.items():
                            player_stats[key] = round(value, 2)

                        player_record = {}
                        player_record["Fantasy Team"] = team_name
                        player_record["Season Year"] = season_year
                        player_record["Season View"] = season_view
                        player_record["Stats View"] = stats_view
                        player_record.update(player_info)
                        player_record.update(player_stats)
                        
                        self.records_df = self.records_df.append(player_record, ignore_index=True)

        return self.records_df