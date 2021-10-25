from espn_data import EspnData

import streamlit as st

st.title('ESPN Fantasy Basketball League Analyzer')

st.markdown("""
A web application that displays data for all players in an ESPN Fantasy League.
* The data is extracted using the [espn-api](https://github.com/cwendt94/espn-api) python package.
""")

espnData = EspnData()
player_records_df = espnData.get_player_records()

col1, col2, col3 = st.columns(3)
season_year = col1.selectbox('Season Year', espnData.season_years)
season_view = col2.selectbox('Season View', espnData.season_views)
stats_view = col3.selectbox('Stats View', espnData.stats_views)

@st.cache
def get_query_df(season_year, season_view, stats_view):
    query = '`Season Year`=="{}" and `Season View`=="{}" and `Stats View`=="{}"'.format(season_year, season_view, stats_view)
    return player_records_df.query(query)

query_df = get_query_df(season_year, season_view, stats_view)
st.dataframe(query_df)