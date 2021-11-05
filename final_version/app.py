from flask import Flask, render_template, request, jsonify
from flask.helpers import url_for
from espn_data import EspnData

app = Flask(__name__)

espnData = EspnData()

@app.route('/')
@app.route('/tables')
def index():
    response = "<h1>List of Season Table Routes</h1>\n"
    response += "<li><a href={}>season</a></li>\n".format(url_for('season'))
    response += "<li><a href={}>team</a></li>\n".format(url_for('team_table'))
    response += "<li><a href={}>draft</a></li>\n".format(url_for('draft'))
    return response

@app.route('/load_season', methods=['POST'])
def load_season():
    if request.method == 'POST':
        season_id = request.json['season_id']
        cats = request.json['cats']
        if cats:
            espnData.calculate_total_zscores(season_id, cats)
        records, zscores, grades = espnData.get_season_data(season_id)
        return jsonify({
            'records': records,
            'zscores': zscores,
            'grades': grades
        })

@app.route('/tables/season')
def season():
    season_ids = espnData.get_season_ids()
    default_season = "2022_curr_avg"
    fantasy_teams = espnData.get_fantasy_teams()
    headers = espnData.get_season_table_headers()
    columns = [{'data': header} for header in headers]
    col_index = {header: i for i, header in enumerate(headers)}
    cats = espnData.cats

    return render_template('season.html',
        season_ids=season_ids, default_season=default_season,
        fantasy_teams=fantasy_teams,
        headers=headers, columns=columns,
        col_index=col_index, cats=cats,
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