from flask.logging import create_logger
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from step_counter.edMQ_client import ProducerClient

from . import config

from ariadne import load_schema_from_path, make_executable_schema, snake_case_fallback_resolvers

app = Flask(__name__)
app.config.from_object(config.settings)
CORS(app)
log = create_logger(app)
log.info('Starting server.')

log.info("Setting up db.")
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from .resolvers import query, mutation

type_defs = load_schema_from_path("step_counter/schema.graphql")
schema = make_executable_schema(
    type_defs, query, mutation, snake_case_fallback_resolvers
)

producer = ProducerClient(app.config['EDMQ_URL'], app.config['SECRET'])
producer.start()

from step_counter.api import routes

