import psycopg

from app.core.config import settings

class DatabaseService:
    
    def connect(self):
        return psycopg.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            dbname=settings.postgres_db,
            user=settings.postgres_user,
            password=settings.postgres_password,
            connect_timeout=10,
        )