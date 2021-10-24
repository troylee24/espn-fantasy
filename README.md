# ESPN-Fantasy

A web application that displays data for all players in an ESPN Fantasy League.

The data is extracted using the [espn-api](https://github.com/cwendt94/espn-api) python package.

## Features
* Displays fantasy team player data for the seasons of 2020-2021 and 2021-2022
* Calculates Z-Score for each player stat based on season year, season view, and stats type
* Maps Z-Score to 3-point gradient color scale (red, white, green)

## Versions
* [sql_version](sql_version) - `Python` `Flask` `HTML/CSS/JS` `SQLite3` `Flask-SQLAlchemy`
  * flask application w/ javascript and jQuery implementations
  * uses an sqlite3 database to store player data
  * url includes query params that can be used to filter database
* [dataframe_version](dataframe_version) - `Python` `Flask` `HTML/CSS/JS`
  * flask application w/ strictly datatables
  * uses pandas dataframes and json as data serialization
* [streamlit_version]() `Python` `Streamlit`
  * *in-progress...*
