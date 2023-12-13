from dotenv import dotenv_values
import psycopg2
config = dotenv_values("../.env")

# basically a database config
class Settings:
    dbname = config['DBNAME']
    user = config['USER']
    password = config['PASSWORD']
    host = config['HOST']
    port = config['PORT']


def connectToDB():
    settings = Settings()
    db = psycopg2.connect(dbname=settings.dbname,
                          user=settings.user,
                          password=settings.password,
                          host=settings.host,
                          port=settings.port)
    return db