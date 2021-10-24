from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from espn import get_filters

app = Flask(__name__)

db_name = 'data/stats.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class Stat(db.Model):
    __tablename__ = 'stats'
    id = db.Column(db.Integer, primary_key=True)
    fantasy_team = db.Column(db.String)
    season = db.Column(db.String)
    season_type = db.Column(db.String)
    stats_type = db.Column(db.String)
    name = db.Column(db.String)
    position = db.Column(db.String)
    proTeam = db.Column(db.String)
    injuryStatus = db.Column(db.String)
    PTS = db.Column(db.Numeric(scale=2))
    BLK = db.Column(db.Numeric(scale=2))
    STL = db.Column(db.Numeric(scale=2))
    AST = db.Column(db.Numeric(scale=2))
    REB = db.Column(db.Numeric(scale=2))
    TO = db.Column(db.Numeric(scale=2))
    FGM = db.Column(db.Numeric(scale=2))
    FGA = db.Column(db.Numeric(scale=2))
    FTM = db.Column(db.Numeric(scale=2))
    FTA = db.Column(db.Numeric(scale=2))
    MPG = db.Column(db.Numeric(scale=2))
    MIN = db.Column(db.Numeric(scale=2))
    GP = db.Column(db.Numeric(scale=2))
    TPTM = db.Column(db.Numeric(scale=2))
    TPTA = db.Column(db.Numeric(scale=2))
    TPTP = db.Column(db.Numeric(scale=2))
    FGP = db.Column(db.Numeric(scale=2))
    FTP = db.Column(db.Numeric(scale=2))

filters = get_filters()

@app.route('/')
def index():
    args = request.args
    stats = Stat.query
    if args:
        if 'fantasy_team' in args:
            fantasy_team = args.get('fantasy_team')
            stats = stats.filter_by(fantasy_team=fantasy_team)
        if 'season' in args:
            season = args.get('season')
            stats = stats.filter_by(season=season)
        if 'season_type' in args:
            season_type = args.get('season_type')
            stats = stats.filter_by(season_type=season_type)
        if 'stats_type' in args:
            stats_type = args.get('stats_type')
            stats = stats.filter_by(stats_type=stats_type)
    return render_template('index.html', stats=stats.all(), filters=filters)

if __name__ == "__main__":
    app.run(debug=True)