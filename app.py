from flask import Flask, render_template
from espn_data import EspnData

app = Flask(__name__)

@app.route('/')
def index():
    espnData = EspnData()
    records, zscores, grades = espnData.from_json()
    return render_template('index.html', records=records, grades=grades)

@app.route('/load')
def load():
    espnData = EspnData()
    espnData.main()
    return '<h1>Data Loaded.</h1>'

if __name__ == "__main__":
    app.run(debug=True)