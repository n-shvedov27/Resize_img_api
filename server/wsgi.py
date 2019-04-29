from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from logging.config import dictConfig
import redis

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO'
    }
})

db = SQLAlchemy()


def create_app(testing=False):
    app = Flask(__name__)
    if not testing:
        pass
        # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        # app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres@localhost:54320/task8'
        # app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

    # db.init_app(app)
    return app


def create_redis_connection():
    r = redis.Redis(
        host='127.0.0.1',
        port=6379
    )
    if not r.exists('id_resized_images'):
        r.set('id_resized_images', 0)
    if not r.exists('id_not_resized_images'):
        r.set('id_not_resized_images', 0)
    return r


from .views import *
