# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import os
import sqlite3
from contextlib import contextmanager

import utils.logColors as lc


@contextmanager
def get_db_connection(db_name, logger):
    conn = sqlite3.connect(db_name)
    try:
        yield conn
    except Exception as e:
        logger.error(f"{lc.r}❌ Database Error: {e}{lc.rs}")
    finally:
        conn.close()


class Database:
    def __init__(self, db_name, logger):
        self.db_name = db_name
        self.logger = logger

    def migration(self):
        with get_db_connection(self.db_name, self.logger) as conn:
            cursor = conn.cursor()
            self.logger.info(f"{lc.b}💽 Database Check and Migration ...{lc.rs}")

            query = "SELECT name FROM sqlite_master WHERE type='table' AND name='migration';"
            cursor.execute(query)
            result = cursor.fetchall()
            if not result:
                self.logger.info(f"{lc.g}└─ 🗒️ Creating migration table ...{lc.rs}")
                query = "CREATE TABLE migration (id INTEGER PRIMARY KEY AUTOINCREMENT, version INTEGER);"
                cursor.execute(query)
                conn.commit()

            migrations = sorted(os.listdir("database_migrations"))
            for migration in migrations:
                if not migration.endswith(".sql"):
                    continue

                sql_id = migration.split(".")[0]
                query = "SELECT * FROM migration WHERE version = ?"
                cursor.execute(query, (sql_id,))
                result = cursor.fetchall()
                if not result:
                    self.logger.info(f"{lc.g}└─ 🔍 Migrating {migration} ...{lc.rs}")
                    with open(f"database_migrations/{migration}", "r") as file:
                        query = file.read()
                        cursor.executescript(query)
                        fileName = migration.split(".")[0]
                        query = "INSERT INTO migration (version) VALUES (?)"
                        cursor.execute(query, (fileName,))
                        conn.commit()

            self.logger.info(f"{lc.g}✅ Database Check and Migration Done!{lc.rs}")

    def migration_modules(self, modules):
        with get_db_connection(self.db_name, self.logger) as conn:
            cursor = conn.cursor()
            self.logger.info(
                f"{lc.b}💽 Database Modules Check and Migration ...{lc.rs}"
            )

            query = "SELECT name FROM sqlite_master WHERE type='table' AND name='modules_migration';"
            cursor.execute(query)
            result = cursor.fetchall()
            if not result:
                self.logger.info(
                    f"{lc.g}└─ 🗒️ Creating modules_migration table ...{lc.rs}"
                )
                query = "CREATE TABLE modules_migration (id INTEGER PRIMARY KEY AUTOINCREMENT, module TEXT, version INTEGER);"
                cursor.execute(query)
                conn.commit()

            for module in modules:
                if not os.path.exists(f"modules/{module}/database_migrations"):
                    continue

                migrations = sorted(os.listdir(f"modules/{module}/database_migrations"))
                for migration in migrations:
                    if not migration.endswith(".sql"):
                        continue

                    query = "SELECT * FROM modules_migration WHERE module = ? AND version = ?"

                    sql_id = migration.split(".")[0]
                    cursor.execute(query, (module, sql_id))
                    result = cursor.fetchall()
                    if not result:
                        self.logger.info(
                            f"{lc.g}└─ 🔍 Migrating {module}/{migration} ...{lc.rs}"
                        )
                        with open(
                            f"modules/{module}/database_migrations/{migration}", "r"
                        ) as file:
                            query = file.read()
                            cursor.executescript(query)
                            fileName = migration.split(".")[0]
                            query = "INSERT INTO modules_migration (module, version) VALUES (?, ?)"
                            cursor.execute(query, (module, fileName))
                            conn.commit()

            self.logger.info(
                f"{lc.g}✅ Database Modules Check and Migration Done!{lc.rs}"
            )

    def query(self, query, data):
        with get_db_connection(self.db_name, self.logger) as conn:
            cursor = conn.cursor()
            cursor.execute(query, data)
            return cursor.fetchall()

    def queryScript(self, query):
        with get_db_connection(self.db_name, self.logger) as conn:
            cursor = conn.cursor()
            cursor.executescript(query)
            return cursor.fetchall()

    def getSettings(self, key, default=None):
        with get_db_connection(self.db_name, self.logger) as conn:
            cursor = conn.cursor()
            query = "SELECT value FROM settings WHERE name = ?"
            cursor.execute(query, (key,))
            result = cursor.fetchall()
            if result:
                return result[0][0]
            return default

    def updateSettings(self, key, value):
        with get_db_connection(self.db_name, self.logger) as conn:
            cursor = conn.cursor()
            query = "INSERT OR REPLACE INTO settings (name, value) VALUES (?, ?)"
            cursor.execute(query, (key, value))
            conn.commit()
            return True

    def deleteSettings(self, key):
        with get_db_connection(self.db_name, self.logger) as conn:
            cursor = conn.cursor()
            query = "DELETE FROM settings WHERE name = ?"
            cursor.execute(query, (key,))
            conn.commit()
            return True
