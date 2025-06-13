from flask import Flask, redirect
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import os

# defining database
db = SQLAlchemy()

#defining migrations
migrate = Migrate()

def create_app():

    # app creating line
    app = Flask(__name__, instance_relative_config=True)

    # configuration
    app.config.from_mapping(
        # this should be changed later, moved to the env file
        JWT_SECRET_KEY = "dev",
        SECRET_KEY = 'dev', 
        SQLALCHEMY_DATABASE_URI='sqlite:///C:/Users/zuzia/Documents/GitHub/collectoback/instance/collecto.sqlite',
        SQLALCHEMY_TRACK_MODIFICATIONS = False,
        RESTX_MASK_SWAGGER = False
    )

    # allowing frontend for query
    CORS(app)

    # db and migration init
    db.init_app(app)
    migrate.init_app(app, db)
    jwt = JWTManager(app)
    
    @app.route('/')
    def home():
        return redirect('/swagger')
    
    authorizations = {
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Add "Bearer &lt;JWT&gt;" to authorize'
        }
    }

    # setup API and Swagger UI
    api = Api(
          app,
          version='1.0',
          title='Collecto API',
          description='API documentation',
          doc='/swagger/',
          default='Default',
          default_label='Default namespace',
          validate=True,
          authorizations=authorizations,
          security='Bearer')

    # registering namespaces
    from .routes.auth import auth_ns as auth_ns
    from .routes.dashboard import dashboard_ns as dashboard_ns
    from .routes.categories import categories_ns as categories_ns
    from .routes.items import items_ns as items_ns
    from .routes.follow import follow_ns as follow_ns
    from .routes.explore import explore_ns as explore_ns
    from .routes.export import export_ns as export_ns
    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(dashboard_ns, path='/dashboard')
    api.add_namespace(categories_ns, path='/categories')
    api.add_namespace(items_ns, path='/items')
    api.add_namespace(follow_ns, path='/follow')
    api.add_namespace(explore_ns, path='/explore')
    api.add_namespace(export_ns, path='/export')
    
    return app