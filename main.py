# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import asyncio
import threading
import time
import os

from flask import json


import utils.logColors as lc
from utils.database import Database
from utils.modules import Module
from utils.webserver import WebServer
import utils.variables as var
import utils.api as api
import utils.utils as utils
import utils.Git as Git

try:
    import config
except ImportError:
    print(
        f"{lc.r}Please create a config.py file with the required variables, check the example file (config.py.sample){lc.rs}"
    )
    raise ImportError(
        "Please create a config.py file with the required variables, check the example file (config.py.sample)"
    )

log = lc.getLogger()

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

    git = Git.Git(log, config.config)
    git_installed = git.CheckGitInstalled()
    if not git_installed:
        log.info(f"{lc.r}🛑 Bot is stopping ... {lc.rs}")
        exit()

    if not os.path.exists("temp"):
        log.info(f"{lc.y}📁 Creating temp directory ...{lc.rs}")
        os.makedirs("temp")

    if not os.path.exists("telegram_accounts"):
        log.info(f"{lc.y}📁 Creating telegram_accounts directory ...{lc.rs}")
        os.makedirs("telegram_accounts")

    # Database connection
    db = Database("database.db", log)
    db.migration()

    licenseType = db.getSettings("license", "Free License")
    licenseTypeMessage = (
        f"{lc.y}{licenseType}{lc.rs}"
        if licenseType == "Free License"
        else f"{lc.c}User License: ***{licenseType[5:20]}...{lc.rs}"
    )
    log.info(f"{lc.g}🔑 Bot License: {lc.rs + licenseTypeMessage}")
    if "free" not in licenseType.lower():
        log.info(f"{lc.g}🔑 Checking license ...{lc.rs}")
        apiObj = api.API(log)
        response = apiObj.ValidateLicense(licenseType)
        if response is not None:
            log.info(
                f"{lc.g}└─ ✅ License validated, Credit: {lc.rs + lc.c + str(response['credit']) + '$' + lc.rs + lc.g}, IP: {lc.rs + lc.c + utils.HideIP(response['ip']) + lc.rs}"
            )
        else:
            log.info(f"{lc.r}└─ ❌ Invalid license key ...{lc.rs}")
            log.info(f"{lc.r}🛑 Bot is stopping ... {lc.rs}")
            return

    # loading modules
    modules = Module(log)
    modules.load_modules()
    db.migration_modules(modules.module_list)

    db.Close()

    if os.path.exists("./telegram_accounts/accounts.json"):
        log.info(f"{lc.g}👤 Reading accounts.json file ...{lc.rs}")
        with open("./telegram_accounts/accounts.json", "r") as f:
            accounts = json.load(f)
            f.close()
            if accounts:
                log.info(
                    f"{lc.g}└─ ✅ Found {lc.rs + lc.c + str(len(accounts)) + lc.rs + lc.g} accounts ...{lc.rs}"
                )

                log.info(f"{lc.g}🔍 Checking session and account files ...{lc.rs}")
                sessions = [
                    f
                    for f in os.listdir("./telegram_accounts")
                    if f.endswith(".session")
                ]
                for session in sessions:
                    if session.replace(".session", "") not in [
                        account["session_name"] for account in accounts
                    ]:
                        log.info(
                            f"{lc.r}└─ ❌ Deleting {session} session file ...{lc.rs}"
                        )
                        os.remove(f"./telegram_accounts/{session}")

                for account in accounts:
                    if not os.path.exists(
                        f"./telegram_accounts/{account['session_name']}.session"
                    ):
                        log.info(
                            f"{lc.r}└─ ❌ {account['session_name']}.session file not found ...{lc.rs}"
                        )
                        accounts.remove(account)

                with open("./telegram_accounts/accounts.json", "w") as f:
                    json.dump(accounts, f, indent=2)

                log.info(f"{lc.g}└─ ✅ Session files are up to date ...{lc.rs}")
            else:
                log.info(f"{lc.r}└─ ❌ No accounts found ...{lc.rs}")
    else:
        log.info(f"{lc.r}└─ ❌ No accounts found ...{lc.rs}")

    # Web server
    web_server = WebServer(log, config.config)
    thread = threading.Thread(target=asyncio.run, args=(web_server.start(),))
    thread.start()

    await asyncio.sleep(1)
    log.info(f"{lc.g}🚀 Bot is ready ... {lc.rs}")

    while True:
        try:
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            log.info(f"{lc.r}🛑 Bot is stopping ... {lc.rs}")
            web_server.stop()
            break


def main():
    asyncio.run(start_bot())


if __name__ == "__main__":
    main()
