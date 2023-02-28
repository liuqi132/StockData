from flask import Flask

from basedata import basedata_blueprint
from config import config
from exts import db
from gkz import gkz_blueprint
from limitup import limit as limit_blueprint
from system_config import system_blueprint
from warehousing import warehousing_blueprint

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
app.register_blueprint(limit_blueprint)
app.register_blueprint(gkz_blueprint)
app.register_blueprint(basedata_blueprint)
app.register_blueprint(system_blueprint)
app.register_blueprint(warehousing_blueprint)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
