class Config():
    SECRET_KEY = 'docplanta'

class DevelopmentConfig(Config):
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'docplanta' 

config={
    'development':DevelopmentConfig
}