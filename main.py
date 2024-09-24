# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import asyncio
import signal
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
from utils.modules_thread import Module_Thread

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
    log.info(f"<green>🚀 Starting MCF ...</green>")

    git = Git.Git(log, config.config)
    git_installed = git.CheckGitInstalled()
    if not git_installed:
        log.info("<red>🛑 Bot is stopping ... </red>")
        exit()

    log.info("<green>🔍 Checking git repository ...</green>")
    localGitCommit = git.GetRecentLocalCommit()
    if localGitCommit is None:
        log.error("<red>🛑 Bot is stopping ... </red>")
        return

    log.info(
        f"<green>└─ ✅ Local Git Commit: </green><cyan>{localGitCommit[:7]}</cyan>"
    )

    apiObj = api.API(log)
    log.info("<green>🌐 Checking MCF version ...</green>")
    mcf_version = apiObj.get_mcf_version()
    commit_hash = None
    commit_date = None
    if mcf_version is not None and "commit_hash" in mcf_version:
        commit_hash = mcf_version["commit_hash"]
        commit_date = mcf_version["commit_date"]
        log.info(
            f"<green>└─ ✅ MCF Version: </green><cyan>{commit_hash[:7]}</cyan><green>, Updated: </green><cyan>{commit_date}</cyan>"
        )

        if not git.GitHasCommit(commit_hash):
            log.warning("<yellow>🔄 Project update is required...</yellow>")
            if utils.getConfig(config.config, "auto_update", True):
                git.UpdateProject()
                log.info("<green>🔄 Project updated successfully ...</green>")
                log.error("<red>🛑 Please restart the bot ... </red>")
                return
            else:
                log.warning("<red>❌ Please update the project...</red>")
                log.info("<red>🛑 Bot is stopping ... </red>")
                return
        else:
            log.info("<green>✅ Project is up to date ...</green>")
    else:
        log.info("<red>└─ ❌ Unable to get MCF version ...</red>")
        log.info("<red>🛑 Bot is stopping ... </red>")
        return

    if not os.path.exists("temp"):
        log.info("<yellow>📁 Creating temp directory ...</yellow>")
        os.makedirs("temp")

    if not os.path.exists("telegram_accounts"):
        log.info("<yellow>📁 Creating telegram_accounts directory ...</yellow>")
        os.makedirs("telegram_accounts")

    # Database connection
    db = Database("database.db", log)
    db.migration()

    licenseType = db.getSettings("license", "Free License")
    licenseTypeMessage = (
        f"<yellow>{licenseType}</yellow>"
        if licenseType == "Free License"
        else f"<cyan>User License: ***{licenseType[5:20]}...</cyan>"
    )
    log.info(f"<green>🔑 Bot License: </green>{licenseTypeMessage}")
    if "free" not in licenseType.lower():
        log.info("<green>🔑 Checking license ...</green>")
        response = apiObj.validate_license(licenseType)
        if (
            response is None
            or "error" in response
            and response.get("status") != "success"
        ):
            log.info("<red>└─ ❌ Unable to validate license key ...</red>")
            log.info("<red>🛑 Bot is stopping ... </red>")
            return

        log.info(
            f"<green>└─ ✅ License validated, Credit: </green><cyan>{str(response['credit'])}$</cyan><green>, IP: </green><cyan>{utils.HideIP(response['ip'])}</cyan>"
        )

    # loading modules
    modules = Module(log)
    modules.load_modules()
    db.migration_modules(modules.module_list)

    modulesThread = Module_Thread(log)
    module_update_thread = None

    if os.path.exists("./telegram_accounts/accounts.json"):
        log.info("<green>👤 Reading accounts.json file (Pyrogram Accounts) ...</green>")
        with open("./telegram_accounts/accounts.json", "r") as f:
            accounts = json.load(f)
            f.close()
            if accounts:
                log.info(
                    f"<green>└─ ✅ Found </green><cyan>{str(len(accounts))}</cyan><green> Pyrogram accounts ...</green>"
                )

                log.info(
                    "<green>🔍 Checking Pyrogram session and account files ...</green>"
                )
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
                            f"<red>└─ ❌ Deleting {session} session file ...</red>"
                        )
                        os.remove(f"./telegram_accounts/{session}")

                for account in accounts:
                    if not os.path.exists(
                        f"./telegram_accounts/{account['session_name']}.session"
                    ):
                        log.info(
                            f"<red>└─ ❌ {account['session_name']}.session file not found ...</red>"
                        )
                        accounts.remove(account)

                with open("./telegram_accounts/accounts.json", "w") as f:
                    json.dump(accounts, f, indent=2)
                    f.close()

                log.info("<green>└─ ✅ Session files are up to date ...</green>")
            else:
                log.info("<red>└─ ❌ No Pyrogram accounts found ...</red>")
        f.close()
    else:
        log.info("<red>└─ ❌ No accounts found ...</red>")

    # Web server
    web_server = WebServer(log, config.config)
    thread = threading.Thread(target=asyncio.run, args=(web_server.start(),))
    thread.start()

    await asyncio.sleep(1)
    log.info("<green>🟢 MCF is ready to use! Check your Web Control Panel.</green>")
    await asyncio.sleep(1)

    if utils.getConfig(config.config, "auto_update_modules", True):
        update_interval = utils.getConfig(config.config, "update_check_interval", 1200)
        if update_interval < 600:
            update_interval = 600
        log.info(
            f"<green>🔄 Auto module update checker is running. Checking every </green><cyan>{update_interval}</cyan><green> seconds.</green>"
        )
        module_update_thread = threading.Thread(
            target=modulesThread.UpdateCheckThread, args=()
        )
        module_update_thread.start()

    modulesThread.RunAllModules()

    while True:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            log.info("<red>🛑 Bot is stopping ... </red>")
            os.kill(os.getpid(), signal.SIGINT)
            # web_server.stop()
            break


def main():
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        log.info("<red>🛑 Bot interrupted by user ... </red>")
        os.kill(os.getpid(), signal.SIGINT)
    except Exception as e:
        log.error(f"<red>🛑 Bot stopped with an error: {e} ... </red>")
        os.kill(os.getpid(), signal.SIGINT)


if __name__ == "__main__":
    main()
