from typing import Tuple, List
from pandas.core.frame import DataFrame
from .functions import zscore, grade

import os
import numpy as np
import json

class TeamTable:
    def __init__(self, team_df: DataFrame, data_dir: str) -> None:
        """by default, should only have cats as columns"""
        self.records_df = team_df
        self.zscores_df: DataFrame = None
        self.grades_df: DataFrame = None
        self.ranks_df: DataFrame = None
    
        self.init_data(data_dir)
        self.calculate_zscores()
        self.to_json()

    def init_data(self, data_dir: str) -> None:
        team_dir = os.path.join(data_dir, 'team')
        self.records_file = os.path.join(team_dir, 'records.json')
        self.zscores_file = os.path.join(team_dir, 'zscores.json')
        self.grades_file = os.path.join(team_dir, 'grades.json')
        self.ranks_file = os.path.join(team_dir, 'ranks.json')

    def to_json(self) -> None:
        self.records_df.to_json(self.records_file, orient='records')
        self.zscores_df.to_json(self.zscores_file, orient='records')
        self.grades_df.to_json(self.grades_file, orient='records')
        self.ranks_df.to_json(self.ranks_file, orient='records')
    
    def get_headers(self) -> Tuple[List[str], List[str]]:
        return list(self.records_df.columns), list(self.ranks_df.columns)
    
    def get_data(self) -> Tuple[dict, dict, dict, dict]:
        with open(self.records_file, 'r') as f:
            records = json.load(f)
        with open(self.zscores_file, 'r') as f:
            zscores = json.load(f)
        with open(self.grades_file, 'r') as f:
            grades = json.load(f)
        with open(self.ranks_file, 'r') as f:
            ranks = json.load(f)
        return records, zscores, grades, ranks

    def calculate_zscores(self) -> None:
        self.zscores_df = self.records_df.copy()
        self.grades_df = self.records_df.copy()
        self.ranks_df = self.records_df.copy()
        
        numeric_cols = self.records_df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            self.zscores_df[col] = zscore(self.zscores_df[col]) if col != 'TO' else zscore(self.zscores_df[col]) * -1
            self.grades_df[col] = self.zscores_df[col].map(lambda z: grade(z))
            self.ranks_df[col] = self.zscores_df[col].rank(ascending=False)

        self.ranks_df['Total'] = self.ranks_df[numeric_cols].sum(axis=1, skipna=False)

        z_col = self.zscores_df[numeric_cols].sum(axis=1, skipna=False)
        z_col = np.trunc(z_col * 100) / 100
        self.records_df['Z'] = z_col
        self.zscores_df['Z'] = zscore(z_col)
        self.grades_df['Z'] = self.zscores_df['Z'].map(lambda z: grade(z))

        rank = self.zscores_df['Z'].rank(ascending=False)
        self.zscores_df.insert(0, 'R', rank)
        self.grades_df.insert(0, 'R', rank)
        self.records_df.insert(0, 'R', rank)
        self.ranks_df.insert(0, 'R', rank)