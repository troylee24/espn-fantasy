from typing import Dict, Tuple, List
from pandas.core.frame import DataFrame
from pandas.core.series import Series

import os
import numpy as np
import math

class SeasonTable:
    def __init__(self, season_year: str, season_view: str, stats_view: str, records_df: DataFrame, cats: list) -> None:
        self.season_year = season_year
        self.season_view = season_view
        self.stats_view = stats_view
        self.cats = cats

        self.records_df = records_df
        self.zscores_df: DataFrame = None
        self.grades_df: DataFrame = None
        
        self.calculate_zscores()
        self.to_json()

    def get_season_id(self) -> str:
        return "{}_{}_{}".format(self.season_year, self.season_view, self.stats_view)

    def to_json(self) -> None:
        if not os.path.exists('data'):
            os.mkdir('data')
        data_dir = "data/{}".format(self.get_season_id())
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)

        records_file = os.path.join(data_dir, 'records.json')
        zscores_file = os.path.join(data_dir, 'zscores.json')
        grades_file = os.path.join(data_dir, 'grades.json')
        
        self.records_df.to_json(records_file, orient='records')
        self.zscores_df.to_json(zscores_file, orient='records')
        self.grades_df.to_json(grades_file, orient='records')
    
    def records_to_dict(self):
        return self.records_df.to_dict(orient='records')
    
    def zscores_to_dict(self):
        return self.zscores_df.to_dict(orient='records')

    def grades_to_dict(self):
        return self.grades_df.to_dict(orient='records')

    ####################################
    ### ZSCORE AND GRADING FUNCTIONS ###
    ####################################

    def zscore(self, col_s: Series) -> Series:
        """Calculates zscore based on a DataFrame column."""
        return (col_s - col_s.mean()) / (col_s.std(ddof=0))

    def zscore_percent(self, df: DataFrame, col: str) -> Series:
        """Calculates zscore for percent stats based on attempted."""
        # i.e. FG% -> FG -> FGA, FGM
        base = col[:-1]
        made, att = base + 'M', base + 'A'

        # calculate impact
        avg_p: Series = df[made].sum()/df[att].sum()
        impact: Series = (df[col] - avg_p)*df[att]

        # calculate zscores of impact
        return self.zscore(impact)
    
    def grade(self, zscore) -> str:
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

    def calculate_zscores(self) -> None:
        self.zscores_df = self.records_df.copy()
        self.grades_df = self.records_df.copy()
        numeric_cols = self.records_df.select_dtypes(include=[np.number])
        
        for col in numeric_cols:
            self.zscores_df[col] = self.zscore_percent(self.records_df, col) if '%' in col else self.zscore(self.records_df[col])
            self.grades_df[col] = self.zscores_df[col].map(lambda z: self.grade(-z)) if col == 'TO' else self.zscores_df[col].map(lambda z: self.grade(z))

        self.calculate_total_zscores(self.cats)

    def calculate_total_zscores(self, cats: List[str]) -> Tuple[DataFrame]:
        self.zscores_df['Z'] = self.zscores_df[cats].sum(axis=1, skipna=False)
        self.zscores_df['Z'] = self.zscore(self.zscores_df['Z']).round(2)
        self.grades_df['Z'] = self.zscores_df['Z'].map(lambda z: self.grade(z))
        self.records_df['Z'] = self.zscores_df['Z'].values

        rank = self.zscores_df['Z'].rank(ascending=False)

        self.zscores_df.drop(columns=['R'], errors='ignore', inplace=True)
        self.grades_df.drop(columns=['R'], errors='ignore', inplace=True)
        self.records_df.drop(columns=['R'], errors='ignore', inplace=True)

        self.zscores_df.insert(0, 'R', rank)
        self.grades_df.insert(0, 'R', rank)
        self.records_df.insert(0, 'R', rank)