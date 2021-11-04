from flask import Flask, render_template, request
from flask.helpers import url_for
from espn_data import EspnData

app = Flask(__name__)

espnData = EspnData()

@app.route('/show_categories', methods=["POST"])
def show_categories():
    if request.method == 'POST':
        season_id = request.json['season_id']
        checked_cats = request.json['checked_cats']
        cats = espnData.cats
        
        cats = [cats[int(cat)] for cat in checked_cats]
        espnData.calculate_total_zscores(season_id, cats)
    return ('', 204)

@app.route('/')
@app.route('/tables')
def index():
    response = "<h1>List of Season Table Routes</h1>\n"
    season_ids = espnData.get_season_ids()
    for season_id in season_ids:
        response += "<li><a href={}>{}</a></li>\n".format(url_for('season_tables', season_id=season_id), season_id)
    response += "<li><a href={}>team</a></li>\n".format(url_for('team_table'))
    response += "<li><a href={}>draft</a></li>\n".format(url_for('draft'))
    return response

@app.route('/tables/season/<string:season_id>')
def season_tables(season_id):
    headers = espnData.get_season_table_headers()
    columns = [{'data': header} for header in headers]
    cats = espnData.cats
    cats_index = { cat: headers.index(cat) for cat in cats }

    return render_template('season_tables.html',
        season_id=season_id,
        headers=headers, columns=columns,
        cats=cats, cats_index=cats_index
    )

@app.route('/tables/team')
def team_table():
    record_headers, rank_headers = espnData.get_team_table_headers()
    record_columns = [{'data': header} for header in record_headers]
    rank_columns = [{'data': header} for header in rank_headers]
    
    return render_template('team_table.html',
        record_headers=record_headers, rank_headers=rank_headers,
        record_columns=record_columns, rank_columns=rank_columns
    )

@app.route('/tables/draft')
def draft():
    headers = espnData.get_season_table_headers()
    columns = [{'data': header} for header in headers]
    cats = espnData.cats
    cats_index = { cat: headers.index(cat) for cat in cats }

    return render_template('draft.html',
        season_id="2022_curr_avg",
        headers=headers, columns=columns,
        cats=cats, cats_index=cats_index
    )

if __name__ == "__main__":
    app.run(debug=True)