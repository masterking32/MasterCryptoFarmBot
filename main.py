# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import asyncio
import signal
import threading
import time
import os

import json

import mcf_utils.logColors as lc
from mcf_utils.database import Database
from mcf_utils.modules import Module
from mcf_utils.webserver import WebServer
import mcf_utils.variables as var
import mcf_utils.api as api
import mcf_utils.utils as utils
import mcf_utils.Git as Git
from mcf_utils.modules_thread import Module_Thread

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
    if not git.CheckGitInstalled():
        log.error("<red>🛑 Git is not installed. Bot is stopping ... </red>")
        exit()

    log.info("<green>🔍 Checking git repository ...</green>")
    localGitCommit = git.GetRecentLocalCommit()
    if localGitCommit is None:
        log.error("<red>🛑 Unable to get local git commit. Bot is stopping ... </red>")
        return

    log.info(
        f"<green>└─ ✅ Local Git Commit: </green><cyan>{localGitCommit[:7]}</cyan>"
    )

    apiObj = api.API(log)
    log.info("<green>🌐 Checking MCF version ...</green>")
    mcf_version = apiObj.get_mcf_version()
    if mcf_version and "commit_hash" in mcf_version:
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
                log.error(
                    "<red>❌ Please update the project manually. Bot is stopping ... </red>"
                )
                return
        else:
            log.info("<green>✅ Project is up to date ...</green>")
    else:
        log.error("<red>❌ Unable to get MCF version. Bot is stopping ... </red>")
        return

    os.makedirs("temp", exist_ok=True)
    os.makedirs("telegram_accounts", exist_ok=True)

    db = Database("database.db", log)
    db.migration()

    licenseType = db.getSettings("license", "Free License")
    licenseTypeMessage = (
        f"<yellow>No License</yellow>"
        if licenseType == "Free License"
        else f"<cyan>User License: ***{licenseType[5:20]}...</cyan>"
    )
    log.info(f"<green>🔑 Bot License: </green>{licenseTypeMessage}")
    if "free" not in licenseType.lower():
        log.info("<green>🔑 Checking license ...</green>")
        response = apiObj.validate_license(licenseType)
        if not response or response.get("status") != "success":
            log.error(
                "<red>❌ Unable to validate license key. Bot is stopping ... </red>"
            )
            return

        log.info(
            f"<green>└─ ✅ License validated, Credit: </green><cyan>{response['credit']}$</cyan><green>, IP: </green><cyan>{utils.HideIP(response['ip'])}</cyan>"
        )

    modules = Module(log)
    modules.load_modules()
    db.migration_modules(modules.module_list)

    modulesThread = Module_Thread(log)

    if os.path.exists("./telegram_accounts/accounts.json"):
        log.info("<green>👤 Reading accounts.json file (Pyrogram Accounts) ...</green>")
        with open("./telegram_accounts/accounts.json", "r") as f:
            accounts = json.load(f)
            if accounts:
                log.info(
                    f"<green>└─ ✅ Found </green><cyan>{len(accounts)}</cyan><green> Pyrogram accounts ...</green>"
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

                accounts = [
                    account
                    for account in accounts
                    if os.path.exists(
                        f"./telegram_accounts/{account['session_name']}.session"
                    )
                ]

                with open("./telegram_accounts/accounts.json", "w") as f:
                    json.dump(accounts, f, indent=2)

                log.info("<green>└─ ✅ Session files are up to date ...</green>")

                if len(accounts) > 0:
                    log.info(
                        "<green>🔭 Checking whether the server has access to Telegram...</green>"
                    )
                    access_to_telegram_website = apiObj.check_telegram_access()
                    if access_to_telegram_website:
                        log.info(f"<green>└─ ✅ Server has access to Telegram.</green>")
                    else:
                        log.error(
                            "<red>❌ Device does not have access to Telegram. ❌</red>\n"
                            "<yellow>1. Restart the bot if you believe the device has access to Telegram.</yellow>\n"
                            "<yellow>2. Ensure Telegram is not blocked in your country.</yellow>\n"
                            "<yellow>3. If using a VPN, verify that it is properly routing all requests through the VPN.</yellow>\n"
                            "<yellow>4. Check VPN settings to ensure all traffic is routed through the VPN.</yellow>"
                        )
                        log.error("<red>└─ ⛔ Telegram access check has failed.</red>")
            else:
                log.info(
                    "<yellow>🟨 No Pyrogram accounts found. You can add them or use module accounts ...</yellow>"
                )
    else:
        log.info(
            "<yellow>🟨 No Pyrogram accounts found. You can add them or use module accounts ...</yellow>"
        )

    web_server = WebServer(log, config.config, modulesThread)
    threading.Thread(target=asyncio.run, args=(web_server.start(),)).start()

    await asyncio.sleep(1)
    log.info("<green>🟢 MCF is ready to use! Check your Web Control Panel.</green>")
    await asyncio.sleep(1)

    if utils.getConfig(config.config, "auto_update_modules", True):
        update_interval = max(
            utils.getConfig(config.config, "update_check_interval", 3600), 3600
        )
        log.info(
            f"<green>🔄 Auto module update checker is running. Checking every </green><cyan>{update_interval}</cyan><green> seconds.</green>"
        )
        threading.Thread(target=modulesThread.update_check_thread).start()

    modulesThread.run_all_modules()

    while True:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            log.info("<red>🛑 Bot is stopping ... </red>")
            os.kill(os.getpid(), signal.SIGINT)
            break


def main():
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        log.info("<red>🛑 Bot interrupted by user ... </red>")
    except Exception as e:
        log.error(f"<red>🛑 Bot stopped with an error: {e} ... </red>")

    try:
        os._exit(0)
    except Exception as e:
        log.error(f"<red>🛑 Error while stopping the bot: {e} ... </red>")
        exit()


if __name__ == "__main__":
    main()
