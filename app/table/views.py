from flask import Blueprint, render_template, request, jsonify
from flask.helpers import url_for
from .models.espn_data import EspnData

import os

table = Blueprint('table', __name__,
                 template_folder='templates',
                 static_folder='static')

data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static', 'data'))
espnData = EspnData(data_dir)

@table.route('/load_season', methods=['POST'])
def load_season():
    if request.method == 'POST':
        season_id = request.json['season_id']
        cats = request.json['cats']
        espnData.calculate_total_zscores(season_id, cats)
        records, zscores, grades = espnData.get_season_data(season_id)
        return jsonify({
            'records': records,
            'zscores': zscores,
            'grades': grades
        })
        
@table.route('/load_team', methods=['POST'])
def load_team():
    if request.method == 'POST':
        records, zscores, grades, ranks = espnData.get_team_data()
        return jsonify({
            'records': records,
            'zscores': zscores,
            'grades': grades,
            'ranks': ranks
        })

@table.route('/load_draft', methods=['POST'])
def load_draft():
    if request.method == 'POST':
        season_id = request.json['season_id']
        cats = espnData.cats
        espnData.calculate_total_zscores(season_id, cats)
        records, zscores, grades = espnData.get_season_data(season_id)
        return jsonify({
            'records': records,
            'zscores': zscores,
            'grades': grades
        })

@table.route('/')
def index():
    response = "<h1>List of Season Table Routes</h1>\n"
    response += "<li><a href={}>season</a></li>\n".format(url_for('table.season'))
    response += "<li><a href={}>team</a></li>\n".format(url_for('table.team'))
    response += "<li><a href={}>draft</a></li>\n".format(url_for('table.draft'))
    return response

@table.route('/season')
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

@table.route('/team')
def team():
    record_headers, rank_headers = espnData.get_team_table_headers()
    record_columns = [{'data': header} for header in record_headers]
    rank_columns = [{'data': header} for header in rank_headers]
    
    return render_template('team.html',
        record_headers=record_headers, rank_headers=rank_headers,
        record_columns=record_columns, rank_columns=rank_columns
    )

@table.route('/draft')
def draft():
    headers = espnData.get_season_table_headers()
    columns = [{'data': header} for header in headers]
    col_index = {header: i for i, header in enumerate(headers)}

    return render_template('draft.html',
        season_id="2022_curr_avg",
        headers=headers, columns=columns,
        col_index=col_index
    )