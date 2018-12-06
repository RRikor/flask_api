# http://flask.pocoo.org/docs/1.0/tutorial/database/

import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    """
    Creates a connection to the database
    """
    # g: saves the connection to handle multiple calls to get_db 
    #   closing the connection
    if 'db' not in g:
        # Makes a connection to the file at the DATABASE config key
        g.db = sqlite3.connect(
            # current_app: points to Flask application handling the request
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Return rows as dicts
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    """
    Closes the connection if g.db is set
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    # open_resource: opens the file relative to flaskr path
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# Calls the CLI-command init-db
@click.command('init-db')
@with_appcontext
def init_db_command():
    "Wipe the database and recreate"
    init_db()
    click.echo("Initialized database")

def init_app(app):
    """
    Does the registration of close_db and init_db_command functions.
    """
    # Tells flask to call function after returning the response
    app.teardown_appcontext(close_db)
    # Adds a new command to be called with the flask command
    app.cli.add_command(init_db_command)


