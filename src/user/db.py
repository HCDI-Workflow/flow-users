import os
import logging
import psycopg2, pprint
from flask import g, current_app
from flask.cli import with_appcontext
import click
from google.cloud.sql.connector import Connector, IPTypes
import pg8000

import sqlalchemy


class DatabaseManager:
    def __init__(self):
        self.logger = logging.getLogger()

    def connect_with_connector(self, is_local=True) -> sqlalchemy.engine.base.Engine:
        if is_local:
            return self.connect_with_local()
        return self.connect_with_cloud()

    def connect_with_local(self) -> sqlalchemy.engine.base.Engine:
        """
            Initializes a connection pool for the LOCAL database.
        """
        db_user = current_app.config["LOCAL_DB_USER"]  # e.g. 'my-db-user'
        db_pass = current_app.config["LOCAL_DB_PASS"]  # e.g. 'my-db-password'
        db_name = current_app.config["LOCAL_DB_NAME"]  # e.g. 'my-database'

        def getconn() -> pg8000.dbapi.Connection:
            conn: pg8000.dbapi.Connection = pg8000.connect(
                user=db_user,
                password=db_pass,
                database=db_name,
            )
            return conn

        if 'pool' not in g:
            g.pool = sqlalchemy.create_engine(
                "postgresql+pg8000://",
                creator=getconn,
                pool_size=5,
                max_overflow=2,
                pool_timeout=30,
                pool_recycle=1800,
            )
            self.logger.info(f"Connected to DB")
        return g.pool

    def connect_with_cloud(self) -> sqlalchemy.engine.base.Engine:
        """
        Initializes a connection pool for a Cloud SQL instance of Postgres.
        Uses the Cloud SQL Python Connector package.
        """
        # Note: Saving credentials in environment variables is convenient, but not
        # secure - consider a more secure solution such as
        # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
        # keep secrets safe.
        instance_connection_name = current_app.config[
            "INSTANCE_CONNECTION_NAME"
        ]  # e.g. 'project:region:instance'
        db_user = current_app.config["DB_USER"]  # e.g. 'my-db-user'
        db_pass = current_app.config["DB_PASS"]  # e.g. 'my-db-password'
        db_name = current_app.config["DB_NAME"]  # e.g. 'my-database'

        ip_type = IPTypes.PRIVATE if current_app.config.get("PRIVATE_IP") else IPTypes.PUBLIC

        # initialize Cloud SQL Python Connector object
        connector = Connector()

        def getconn() -> pg8000.dbapi.Connection:
            conn: pg8000.dbapi.Connection = connector.connect(
                instance_connection_name,
                "pg8000",
                user=db_user,
                password=db_pass,
                db=db_name,
                ip_type=ip_type,
            )
            return conn

        # The Cloud SQL Python Connector can be used with SQLAlchemy
        # using the 'creator' argument to 'create_engine'
        if 'pool' not in g:
            g.pool = sqlalchemy.create_engine(
                "postgresql+pg8000://",
                creator=getconn,
                # [START_EXCLUDE]
                # Pool size is the maximum number of permanent connections to keep.
                pool_size=5,
                # Temporarily exceeds the set pool_size if no connections are available.
                max_overflow=2,
                # The total number of concurrent connections for your application will be
                # a total of pool_size and max_overflow.
                # 'pool_timeout' is the maximum number of seconds to wait when retrieving a
                # new connection from the pool. After the specified amount of time, an
                # exception will be thrown.
                pool_timeout=30,  # 30 seconds
                # 'pool_recycle' is the maximum number of seconds a connection can persist.
                # Connections that live longer than the specified amount of time will be
                # re-established
                pool_recycle=1800,  # 30 minutes
                # [END_EXCLUDE]
            )
            self.logger.info(f"Connected to DB")
        return g.pool

    def close_db(self, e=None):
        db = g.pop('pool', None)

        if db is not None:
            db.dispose()
        self.logger.info("DB Connection Closed.")

    def init_db(self):
        pool = self.connect_with_connector()
        with current_app.open_resource('schema.sql') as f:
            sql_statement = f.read().decode('utf8').split(';')
            with pool.connect() as cursor:
                transaction = cursor.begin()
                for command in sql_statement:
                    cursor.execute(sqlalchemy.text(command + ";"))
                transaction.commit()
        self.close_db()

    @click.command('init-db')
    @with_appcontext
    def init_db_command(self):
        """Clear existing data and create new tables."""
        self.init_db()
        click.echo('Initialized the database.')

    def init_app(self, app):
        app.teardown_appcontext(self.close_db)
        app.cli.add_command(self.init_db_command)