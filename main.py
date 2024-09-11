# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import asyncio
import logging
import threading
import time
import os

from colorlog import ColoredFormatter


import utils.logColors as lc
from utils.database import Database
from utils.modules import Module
from utils.webserver import WebServer
import utils.variables as var

try:
    import config
except ImportError:
    print(
        f"{lc.r}Please create a config.py file with the required variables, check the example file (config.py.sample){lc.rs}"
    )
    raise ImportError(
        "Please create a config.py file with the required variables, check the example file (config.py.sample)"
    )

# ---------------------------------------------#
# Logging configuration
LOG_LEVEL = logging.DEBUG
# Include date and time in the log format
LOGFORMAT = f"{lc.cb}[MasterCryptoBot]{lc.rs} {lc.bt}[%(asctime)s]{lc.bt} %(log_color)s[%(levelname)s]%(reset)s %(log_color)s%(message)s%(reset)s"

logging.root.setLevel(LOG_LEVEL)
formatter = ColoredFormatter(
    LOGFORMAT, "%Y-%m-%d %H:%M:%S"
)  # Specify the date/time format
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(formatter)
log = logging.getLogger("pythonConfig")
log.setLevel(LOG_LEVEL)
log.addHandler(stream)
# End of configuration
# ---------------------------------------------#

banner = f"""
{lc.m}
▓▓▓▓     ▓▓▓▓▓▓       ▓▓▓▓▓▓▓▓▓▓▓▓       ▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓    ▓▓▓▓▓▓      ▓▓▓▓      ▓▓▓       ▓▓▓▓
▓▓▓▓▓   ▓▓▓▓▓▓▓      ▓▓▓                 ▓▓▓▓
▓▓ ▓▓▓ ▓▓▓▓▓▓▓▓     ▓▓▓▓                 ▓▓▓▓▓▓▓▓▓▓
▓▓ ▓▓▓▓▓▓▓ ▓▓▓▓      ▓▓▓         ▓▓      ▓▓▓▓
▓▓  ▓▓▓▓▓▓ ▓▓▓▓      ▓▓▓▓▓    ▓▓▓▓       ▓▓▓▓
▓▓   ▓▓▓▓  ▓▓▓▓        ▓▓▓▓▓▓▓▓▓▓        ▓▓▓▓
{lc.rs}
            {lc.b}🤖 MasterCryptoFarmBot {lc.rs + lc.c}v{var.APP_VERSION} 🤖{lc.rs}
            {lc.b}👉 Created by: {lc.rs + lc.r}MasterkinG32 👈{lc.rs}
    {lc.b}🌍 Telegram: {lc.rs + lc.g}https://t.me/MasterCryptoFarmBot 🌍{lc.rs}
            ⛔ {lc.rb}CTRL + C to STOP THE BOT! {lc.rs}⛔

"""
print(banner)


async def start_bot():
    log.info(f"{lc.g}🚀 Bot is running ...{lc.rs}")

    if not os.path.exists("temp"):
        log.info(f"{lc.y}📁 Creating temp directory ...{lc.rs}")
        os.makedirs("temp")

    # Database connection
    db = Database("database.db", log)
    db.migration()

    # loading modules
    modules = Module(log, db)
    modules.load_modules()
    db.migration_modules(modules.module_list)

    # Web server
    web_server = WebServer(log, db, config.config)
    thread = threading.Thread(target=asyncio.run, args=(web_server.start(),))
    thread.start()

    await asyncio.sleep(1)
    log.info(f"{lc.g}🚀 Bot is ready ... {lc.rs}")

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            log.info(f"{lc.r}🛑 Bot is stopping ... {lc.rs}")
            web_server.stop()
            break


def main():
    asyncio.run(start_bot())


if __name__ == "__main__":
    main()
