# http://flask.pocoo.org/docs/1.0/tutorial/factory/

import os
from flask import Flask

def create_app(test_config=None):
        """
        Creates the Flask Application Factory
        """
        # __name__: name of current python module (convention)
        # instance_relative_config: config files are relative to instance folder
        app = Flask(__name__, instance_relative_config=True)
        app.config.from_mapping(
            # Key to keep data safe, should be random on deployment
            SECRET_KEY='dev',
            # path where DB will be saved
            DATABASE=os.path.join(app.instance_path, 'flaskr_sqlite')
        )

        # If the test_config is not there, load the instance config
        # Else load the config.py. This overrides default configuration
        if test_config is None:
            app.config.from_pyfile('config.py', silent=True)
        else:
            app.config.from_mapping(test_config)

        # Make sure the instance folder exists because the DB will be saved here
        try:
            os.makedirs(app.instance_path)
        except OSError:
            pass

        #Hello world page
        @app.route('/hello')
        def hello():
            return 'Hello World!'

        # Register init so it is available as CLI
        from . import db
        db.init_app(app)

        # Register the auth blueprint
        from . import auth
        app.register_blueprint(auth.bp)
        
        return app

