import numpy as np
from pandas.core.frame import DataFrame

import math
import pandas as pd
from pandas.core.series import Series

pd.options.mode.chained_assignment = None

def zscore(col: Series) -> Series:
    """Calculates zscore for column"""
    zscore_col = (col - col.mean()) / (col.std(ddof=0))
    return np.trunc(zscore_col * 100) / 100

def impact(df: DataFrame, col: Series) -> Series:
    """Calculates impact for percent stat based on attempted."""
    # i.e. FG% -> FG -> FGA, FGM
    base = col[:-1]
    made, att = base + 'M', base + 'A'

    # calculate impact
    avg_p = df[made].sum()/df[att].sum()
    impact = (df[col] - avg_p)*df[att]
    return impact

def grade(zscore) -> str:
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