import json
from flask import Flask, render_template
from espn_data import json_to_data

app = Flask(__name__)

@app.route('/')
def index():
    
    data, grades = json_to_data()
    return render_template('index.html', data=data, grades=grades)

if __name__ == "__main__":
    app.run(debug=True)