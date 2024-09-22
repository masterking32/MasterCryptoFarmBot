# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import os
import sqlite3

import utils.logColors as lc


class Database:
    def __init__(self, db_name, logger):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.logger = logger

    def migration(self):
        self.logger.info(f"{lc.b}💽 Database Check and Migration ...{lc.rs}")

        query = (
            "SELECT name FROM sqlite_master WHERE type='table' AND name='migration';"
        )
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        if not result:
            self.logger.info(f"{lc.g}└─ 🗒️ Creating migration table ...{lc.rs}")
            query = "CREATE TABLE migration (id INTEGER PRIMARY KEY AUTOINCREMENT, version INTEGER);"
            self.cursor.execute(query)
            self.conn.commit()

        migrations = sorted(os.listdir("database_migrations"))
        for migration in migrations:
            if not migration.endswith(".sql"):
                continue

            sql_id = migration.split(".")[0]
            query = "SELECT * FROM migration WHERE version = ?"
            self.cursor.execute(query, (sql_id,))
            result = self.cursor.fetchall()
            if not result:
                self.logger.info(f"{lc.g}└─ 🔍 Migrating {migration} ...{lc.rs}")
                with open(f"database_migrations/{migration}", "r") as file:
                    query = file.read()
                    self.cursor.executescript(query)
                    fileName = migration.split(".")[0]
                    query = "INSERT INTO migration (version) VALUES (?)"
                    self.cursor.execute(query, (fileName,))
                    self.conn.commit()
                    file.close()

        self.logger.info(f"{lc.g}✅ Database Check and Migration Done!{lc.rs}")

    def migration_modules(self, modules):
        self.logger.info(f"{lc.b}💽 Database Modules Check and Migration ...{lc.rs}")

        query = "SELECT name FROM sqlite_master WHERE type='table' AND name='modules_migration';"

        self.cursor.execute(query)
        result = self.cursor.fetchall()
        if not result:
            self.logger.info(f"{lc.g}└─ 🗒️ Creating modules_migration table ...{lc.rs}")
            query = "CREATE TABLE modules_migration (id INTEGER PRIMARY KEY AUTOINCREMENT, module TEXT, version INTEGER);"
            self.cursor.execute(query)
            self.conn.commit()

        for module in modules:
            if not os.path.exists(f"modules/{module}/database_migrations"):
                continue

            migrations = sorted(os.listdir(f"modules/{module}/database_migrations"))
            for migration in migrations:
                if not migration.endswith(".sql"):
                    continue

                query = (
                    "SELECT * FROM modules_migration WHERE module = ? AND version = ?"
                )

                sql_id = migration.split(".")[0]
                self.cursor.execute(query, (module, sql_id))
                result = self.cursor.fetchall()
                if not result:
                    self.logger.info(
                        f"{lc.g}└─ 🔍 Migrating {module}/{migration} ...{lc.rs}"
                    )
                    with open(
                        f"modules/{module}/database_migrations/{migration}", "r"
                    ) as file:
                        query = file.read()
                        self.cursor.executescript(query)
                        fileName = migration.split(".")[0]
                        query = "INSERT INTO modules_migration (module, version) VALUES (?, ?)"
                        self.cursor.execute(query, (module, fileName))
                        self.conn.commit()
                        file.close()

        self.logger.info(f"{lc.g}✅ Database Modules Check and Migration Done!{lc.rs}")

    def query(self, query, data):
        self.cursor.execute(query, data)
        return self.cursor.fetchall()

    def queryScript(self, query):
        self.cursor.executescript(query)
        return self.cursor.fetchall()

    def getSettings(self, key, default=None):
        query = "SELECT value FROM settings WHERE name = ?"
        self.cursor.execute(query, (key,))
        result = self.cursor.fetchall()
        if result:
            return result[0][0]
        return default

    def updateSettings(self, key, value):
        query = "INSERT OR REPLACE INTO settings (name, value) VALUES (?, ?)"
        self.cursor.execute(query, (key, value))
        self.conn.commit()
        return True

    def deleteSettings(self, key):
        query = "DELETE FROM settings WHERE name = ?"
        self.cursor.execute(query, (key,))
        self.conn.commit()
        return True

    def __del__(self):
        try:
            self.conn.close()
        except Exception as e:
            pass

    def Close(self):
        try:
            self.conn.close()
            self.logger.info(f"{lc.r}🔌 Database Connection Closed!{lc.rs}")
        except Exception as e:
            pass
