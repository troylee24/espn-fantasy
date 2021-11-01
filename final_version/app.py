from flask import Flask, render_template, request, jsonify
from flask.helpers import url_for
from espn_data import EspnData, get_grades

app = Flask(__name__)

espnData = EspnData()
espnData.create_season_tables()
cats = espnData.cats

@app.route('/show_categories', methods=["POST"])
def show_categories():
    if request.method == 'POST':
        season_id = request.json['season_id']
        checked_cats = request.json['checked_cats']
        data = [cats[int(cat)] for cat in checked_cats]
        espnData.calculate_total_zscores(data)
        return jsonify(get_grades(season_id))

@app.route('/')
@app.route('/tables')
def index():
    response = "<h1>List of Season Table Routes</h1>\n"
    season_ids = espnData.get_season_ids()
    for season_id in season_ids:
        response += "<li><a href={}>{}</a></li>\n".format(url_for('tables', season_id=season_id), season_id)
    return response

@app.route('/tables/<string:season_id>')
def tables(season_id):
    grades = get_grades(season_id)
    headers = list(grades[0].keys())
    columns = [{'data': header} for header in headers]
    cats_index = { cat: headers.index(cat) for cat in cats }

    return render_template('tables.html',
        season_id=season_id, grades=grades,
        headers=headers, columns=columns,
        cats=cats, cats_index=cats_index
    )

if __name__ == "__main__":
    app.run(debug=True)