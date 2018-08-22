import sqlalchemy

Session = sqlalchemy.orm.sessionmaker()

class Database:
    def __init__(self, database_url):
        self.engine = sqlalchemy.create_engine(database_url, echo=False)
        self.session = Session(bind=self.engine)
