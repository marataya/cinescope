import os

from dotenv import load_dotenv

# грузит.env из корня проекта
load_dotenv()

class DBCreds:
    HOST = os.getenv("DB_MOVIES_HOST")
    PORT = os.getenv("DB_MOVIES_PORT")
    NAME = os.getenv("DB_MOVIES_NAME")
    USER = os.getenv("DB_MOVIES_USER")
    PASSWORD = os.getenv("DB_MOVIES_PASSWORD")

    # @classmethod
    # def get_connection_string(cls):
    #     return f"postgresql://{cls.USER}:{cls.PASSWORD}@{cls.HOST}:{cls.PORT}/{cls.NAME}"
    #
    # @classmethod
    # def get_psycopg_dict(cls):
    #     return {
    #         "host": cls.HOST,
    #         "port": cls.PORT,
    #         "dbname": cls.NAME,
    #         "user": cls.USER,
    #         "password": cls.PASSWORD,
    #     }