from flask import Flask, render_template
from espn_data import EspnData

app = Flask(__name__)

@app.route('/reload_data')
def reload_data():
    espnData = EspnData()
    espnData.run_api()
    return ('', 204)

@app.route('/')
def test():
    espnData = EspnData()
    records, zscores, grades = espnData.from_json()
    cols = list(records[0].keys())
    columns = []
    for col in cols:
        columns.append({'data': col})
    return render_template('index.html', records=records, cols=cols, columns=columns, zscores=zscores, grades=grades)

if __name__ == "__main__":
    app.run(debug=True)