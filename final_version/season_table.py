from typing import Tuple, List
from flask import json
from pandas.core.frame import DataFrame
from zscore import zscore, impact, grade

import os
import numpy as np

class SeasonTable:
    def __init__(self, season_id: str, records_df: DataFrame, cats: list) -> None:
        self.season_id = season_id
        self.cats = cats

        self.records_df = records_df
        self.zscores_df: DataFrame = None
        self.grades_df: DataFrame = None

        self.init_data()
        self.calculate_zscores()
        self.to_json()
    
    def init_data(self) -> None:
        data_dir = os.path.join('static', 'data', 'season')
        season_dir = os.path.join(data_dir, self.season_id)
        if not os.path.exists(season_dir):
            os.mkdir(season_dir)

        self.records_file = os.path.join(season_dir, 'records.json')
        self.zscores_file = os.path.join(season_dir, 'zscores.json')
        self.grades_file = os.path.join(season_dir, 'grades.json')

    def get_headers(self) -> List[str]:
        return list(self.records_df.columns)

    def get_data(self) -> Tuple[dict, dict, dict]:
        with open(self.records_file) as f:
            records = json.load(f)
        with open(self.zscores_file) as f:
            zscores = json.load(f)
        with open(self.grades_file) as f:
            grades = json.load(f)
        return records, zscores, grades

    def to_json(self) -> None:        
        self.records_df.to_json(self.records_file, orient='records')
        self.zscores_df.to_json(self.zscores_file, orient='records')
        self.grades_df.to_json(self.grades_file, orient='records')    

    def calculate_zscores(self) -> None:
        self.zscores_df = self.records_df.copy()
        self.grades_df = self.records_df.copy()
        
        numeric_cols = self.records_df.select_dtypes(include=[np.number]).columns
        stat_percent_cols = [col for col in numeric_cols if '%' in col]

        for col in stat_percent_cols:
            self.zscores_df[col] = impact(self.zscores_df, col)
        for col in numeric_cols:
            self.zscores_df[col] = zscore(self.zscores_df, col) if col != 'TO' else zscore(self.zscores_df, col) * -1
            self.grades_df[col] = self.zscores_df[col].map(lambda z: grade(z))

        # make space for rank column
        self.zscores_df.insert(0, 'R', 0)
        self.grades_df.insert(0, 'R', 0)
        self.records_df.insert(0, 'R', 0)

        self.calculate_total_zscores(self.cats)

    def calculate_total_zscores(self, cats: List[str]) -> Tuple[DataFrame]:
        self.zscores_df['Z'] = self.zscores_df[cats].sum(axis=1, skipna=False)
        self.records_df['Z'] = np.trunc(100 * self.zscores_df['Z']) / 100
        self.zscores_df['Z'] = zscore(self.zscores_df, 'Z')
        self.grades_df['Z'] = self.zscores_df['Z'].map(lambda z: grade(z))

        rank = self.zscores_df['Z'].rank(ascending=False)
        self.zscores_df['R'] = rank
        self.grades_df['R'] = rank
        self.records_df['R'] = rank