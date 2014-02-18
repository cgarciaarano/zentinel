from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from zentinel.web import web,db

migrate = Migrate(web, db)

manager = Manager(web)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
	manager.run()