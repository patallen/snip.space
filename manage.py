from app import app, db
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from commands import CreateSuperuser, SeedDatabase

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('createsuperuser', CreateSuperuser())
manager.add_command('seed', SeedDatabase())

if __name__ == '__main__':
    manager.run()
