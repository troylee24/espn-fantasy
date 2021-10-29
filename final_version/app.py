from flask import Flask, render_template, request
from espn_data import EspnData, get_data

app = Flask(__name__)

espnData = EspnData()
espnData.create_season_tables()
cats = espnData.cats

@app.route('/reload_data', methods=["POST"])
def reload_data():
    if request.method == 'POST':
        data = request.json
        data = [cats[int(cat)] for cat in data]
        espnData.calculate_total_zscores(data)
    return ('', 204)

@app.route('/')
def index():
    names_tables, records_tables, zscores_tables, grades_tables = get_data()
    headers = list(records_tables[0][0].keys())
    columns = [{'data': header} for header in headers]
    
    return render_template('index.html', names_tables=names_tables, headers=headers, columns=columns, records_tables=records_tables, zscores_tables=zscores_tables, grades_tables=grades_tables, cats=cats)

if __name__ == "__main__":
    app.run(debug=True)