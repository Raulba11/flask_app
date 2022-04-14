from flask_migrate import Migrate
import sqlalchemy


def setup(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:19102002@localhost:5432/mycalc"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = "TRUE"
    app.config['SECRET_KEY'] = "e7448807977695aa309a9ab809783bc7d92ef114edf11fb437018de58d54e77ceabb65aa05ea3e58f3b4ac5b5b3b903f23117b0cfaeb9ec10e21695430745488"
    
