# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import json
import os
import hashlib
import base64
from flask import redirect, render_template, session

from utils.database import Database
import utils.variables as vr
import utils.Git as Git
import utils.logColors as lc
import utils.api as api


class admin:
    def dashboard(self, request, webServer):
        if "admin" not in session:
            return redirect("/auth/login.py")
        Last_Update = "..."

        db = Database("database.db", webServer.logger)
        license = db.getSettings("license", "Free License")
        db.Close()
        git = Git.Git(webServer.logger, webServer.config)
        github_commit = git.GetGitHubRecentCommit(vr.GITHUB_REPOSITORY)
        local_commit = git.GetRecentLocalCommit()
        webServer.local_git_commit = local_commit
        webServer.github_git_commit = github_commit
        Update_Available = True

        if webServer.github_git_commit != None:
            Last_Update = webServer.github_git_commit["commit"]["author"]["date"]
            Last_Update = Last_Update.replace("T", " ").replace("Z", "")
            if (
                webServer.local_git_commit != None
                and webServer.local_git_commit == webServer.github_git_commit["sha"]
            ):
                Update_Available = False
        else:
            Last_Update = "Failed to fetch GitHub commit"
            Update_Available = False

        if webServer.local_git_commit == None:
            Last_Update = "Failed to fetch local commit, Please initialize git"
            Update_Available = True

        return render_template(
            "admin/dashboard.html",
            Server_IP=webServer.public_ip,
            App_Version=vr.APP_VERSION,
            Last_Update=Last_Update,
            Update_Available=Update_Available,
            License=license,
        )

    def settings(self, request, webServer):
        if "admin" not in session:
            return redirect("/auth/login.py")

        error = None
        success = None

        db = Database("database.db", webServer.logger)
        license = db.getSettings("license", "Free License")
        if request.method == "POST" and "action" in request.form:
            if (
                "current-password" in request.form
                and "new-password" in request.form
                and "confirm-password" in request.form
            ):
                if db.getSettings("admin_password") != request.form["current-password"]:
                    error = "Current password is incorrect!"
                elif request.form["new-password"] == request.form["confirm-password"]:
                    db.updateSettings("admin_password", request.form["new-password"])

                    success = "Password changed successfully."
                    webServer.logger.info(
                        f"{lc.g}🔑 Admin password changed successfully, New password: {lc.rs + lc.c + request.form['new-password'] + lc.rs}"
                    )
                else:
                    error = "New password and confirm password does not match."

            else:
                error = "Please fill all the fields."

        db.Close()
        return render_template(
            "admin/settings.html",
            error=error,
            success=success,
            server_ip=webServer.public_ip,
            license=license,
        )

    def accounts(self, request, webServer):
        if "admin" not in session:
            return redirect("/auth/login.py")

        accounts = []
        success = ""
        error = ""
        with open("telegram_accounts/accounts.json", "r") as f:
            accounts = json.load(f)

        if "disable" in request.args:
            AccountID = request.args.get("disable", 0)
            for account in accounts:
                if str(account["id"]) == str(AccountID):
                    success = (
                        f"Account {account['session_name']} disabled successfully."
                    )
                    account["disabled"] = True
                    webServer.logger.info(
                        f"{lc.r}🔒 Account disabled, Account ID: {lc.rs + lc.c + AccountID + lc.rs}"
                    )
                    break

            with open("telegram_accounts/accounts.json", "w") as f:
                json.dump(accounts, f, indent=4)

        if "enable" in request.args:
            AccountID = request.args.get("enable", 0)
            for account in accounts:
                if str(account["id"]) == str(AccountID):
                    success = f"Account {account['session_name']} enabled successfully."
                    webServer.logger.info(
                        f"{lc.g}🔓 Account enabled, Account ID: {lc.rs + lc.c + AccountID + lc.rs}"
                    )
                    account["disabled"] = False
                    break

            with open("telegram_accounts/accounts.json", "w") as f:
                json.dump(accounts, f, indent=4)

        if request.method == "POST" and "account_id" in request.form:
            AccountID = request.form["account_id"]
            for account in accounts:
                if str(account["id"]) == str(AccountID):
                    account["user_agent"] = (
                        ""
                        if "user_agent" not in request.form
                        else request.form["user_agent"]
                    )
                    account["proxy"] = (
                        "" if "proxy" not in request.form else request.form["proxy"]
                    )

                    success = f"Account {account['session_name']} updated successfully."
                    webServer.logger.info(
                        f"{lc.g}🔄 Account updated, Account ID: {lc.rs + lc.c + AccountID + lc.rs}"
                    )
                    break

            with open("telegram_accounts/accounts.json", "w") as f:
                json.dump(accounts, f, indent=4)

        return render_template(
            "admin/accounts.html",
            accounts=accounts,
            SystemOS=webServer.SystemOS,
            error=error,
            success=success,
        )

    def change_license(self, request, webServer):
        if "admin" not in session:
            return redirect("/auth/login.py")

        error = None
        success = None

        db = Database("database.db", webServer.logger)
        license = db.getSettings("license", "Free License")
        credit = None
        if request.method == "POST" and "license" in request.form:
            license_key = request.form["license"]
            apiObj = api.API(webServer.logger)
            response = apiObj.ValidateLicense(license_key)
            if response != None:
                db.updateSettings("license", license_key)
                success = "License updated successfully."
                webServer.logger.info(
                    f"{lc.g}🔑 License updated successfully, New license: {lc.rs + lc.c + license + lc.rs}"
                )
                webServer.logger.info(
                    f"{lc.g}📖 License Credit: {lc.rs + lc.c + str(response['credit']) + '$' + lc.rs + lc.g}, IP: {lc.rs + lc.c + response['ip'] + lc.rs}"
                )
                license = license_key
                credit = response["credit"]
            else:
                error = "Invalid license key."
        db.Close()
        return render_template(
            "admin/change_license.html",
            error=error,
            success=success,
            server_ip=webServer.public_ip,
            license=license,
            credit=credit,
        )

    def bots(self, requests, webServer):
        if "admin" not in session:
            return redirect("/auth/login.py")

        error = None
        success = None

        modules = os.listdir("modules")
        bots = []
        db = Database("database.db", webServer.logger)
        for module in modules:
            if os.path.isdir(f"modules/{module}") and os.path.exists(
                f"modules/{module}/bot.py"
            ):
                bot = {}
                bot["name"] = module
                bot["id"] = hashlib.md5(module.encode()).hexdigest()

                if os.path.exists(f"modules/{module}/logo.png"):
                    with open(f"modules/{module}/logo.png", "rb") as f:
                        logo_data = base64.b64encode(f.read()).decode()
                    bot["logo"] = f"data:image/png;base64,{logo_data}"
                else:
                    bot["logo"] = ""

                bot["disabled"] = db.getSettings(f"{module}_disabled", False)

                if os.path.exists(f"modules/{module}/bot_settings.json"):
                    with open(f"modules/{module}/bot_settings.json", "r") as f:
                        bot_settings = json.load(f)
                        bot["settings"] = bot_settings
                else:
                    bot["settings"] = {}

                if os.path.exists(f"modules/{module}/bot_settings_types.json"):
                    with open(f"modules/{module}/bot_settings_types.json", "r") as f:
                        bot_settings = json.load(f)
                        bot["settings_types"] = bot_settings
                else:
                    bot["settings_types"] = None

                accounts = []
                if os.path.exists(f"modules/{module}/accounts.json"):
                    with open(f"modules/{module}/accounts.json", "r") as f:
                        accounts = json.load(f)

                bot["accounts"] = accounts
                bots.append(bot)

        if "disable" in requests.args:
            BotID = requests.args.get("disable", 0)
            for bot in bots:
                if str(bot["id"]) == str(BotID):
                    success = f"Bot {bot['name']} disabled successfully."
                    db.updateSettings(f"{bot['name']}_disabled", True)
                    bots[bots.index(bot)]["disabled"] = True
                    webServer.logger.info(
                        f"{lc.r}🔒 Bot disabled, Bot Name: {lc.rs + lc.c + bot['name'] + lc.rs}"
                    )
                    break
        elif "enable" in requests.args:
            BotID = requests.args.get("enable", 0)
            for bot in bots:
                if str(bot["id"]) == str(BotID):
                    success = f"Bot {bot['name']} enabled successfully."
                    db.deleteSettings(f"{bot['name']}_disabled")
                    bots[bots.index(bot)]["disabled"] = False
                    webServer.logger.info(
                        f"{lc.g}🔓 Bot enabled, Bot Name: {lc.rs + lc.c + bot['name'] + lc.rs}"
                    )
                    break
        elif "delete_account" in requests.args and "bot_id" in requests.args:
            BotID = requests.args.get("bot_id", 0)
            AccountID = requests.args.get("delete_account", 0)
            for bot in bots:
                if str(bot["id"]) == str(BotID):
                    accounts = bot["accounts"]
                    for account in accounts:
                        if str(account["id"]) == str(AccountID):
                            success = (
                                f"Account {account['display_name']} deleted successfully."
                            )
                            accounts.remove(account)
                            with open(f"modules/{bot['name']}/accounts.json", "w") as f:
                                json.dump(accounts, f, indent=4)
                            bots[bots.index(bot)]["accounts"] = accounts
                            webServer.logger.info(
                                f"{lc.r}🗑 Account deleted, Bot Name: {lc.rs + lc.c + bot['name'] + lc.rs + lc.r}, Session Name: {lc.rs + lc.c + account['display_name'] + lc.rs}"
                            )
                            break
        elif "disable_account" in requests.args and "bot_id" in requests.args:
            BotID = requests.args.get("bot_id", 0)
            AccountID = requests.args.get("disable_account", 0)
            for bot in bots:
                if str(bot["id"]) == str(BotID):
                    accounts = bot["accounts"]
                    for account in accounts:
                        if str(account["id"]) == str(AccountID):
                            success = (
                                f"Account {account['display_name']} disabled successfully."
                            )
                            account["disabled"] = True
                            with open(f"modules/{bot['name']}/accounts.json", "w") as f:
                                json.dump(accounts, f, indent=4)
                            bots[bots.index(bot)]["accounts"] = accounts
                            webServer.logger.info(
                                f"{lc.r}🔒 Account disabled, Bot Name: {lc.rs + lc.c + bot['name'] + lc.rs + lc.r}, Session Name: {lc.rs + lc.c + account['display_name'] + lc.rs}"
                            )
                            break
        elif "enable_account" in requests.args and "bot_id" in requests.args:
            BotID = requests.args.get("bot_id", 0)
            AccountID = requests.args.get("enable_account", 0)
            for bot in bots:
                if str(bot["id"]) == str(BotID):
                    accounts = bot["accounts"]
                    for account in accounts:
                        if str(account["id"]) == str(AccountID):
                            success = (
                                f"Account {account['display_name']} enabled successfully."
                            )
                            account["disabled"] = False
                            with open(f"modules/{bot['name']}/accounts.json", "w") as f:
                                json.dump(accounts, f, indent=4)
                            bots[bots.index(bot)]["accounts"] = accounts
                            webServer.logger.info(
                                f"{lc.g}🔓 Account enabled, Bot Name: {lc.rs + lc.c + bot['name'] + lc.rs + lc.g}, Session Name: {lc.rs + lc.c + account['display_name'] + lc.rs}"
                            )

        if requests.method != "POST":
            db.Close()
            return render_template(
                "admin/bots.html", error=error, success=success, bots=bots
            )

        if "bot_id" in requests.form:
            BotID = requests.form["bot_id"]
            settings = {}
            for bot in bots:
                if str(bot["id"]) == str(BotID):
                    for key in requests.form:
                        if key != "bot_id":
                            settings[key] = requests.form[key]

                    with open(f"modules/{bot['name']}/bot_settings.json", "w") as f:
                        json.dump(settings, f, indent=4)
                    bots[bots.index(bot)]["settings"] = settings
                    success = f"Bot {bot['name']} updated successfully."
                    webServer.logger.info(
                        f"{lc.g}🔄 Bot updated, Bot Name: {lc.rs + lc.c + bot['name'] + lc.rs}"
                    )
                    break

        if "add_account" in requests.form:
            BotID = requests.form["add_account"]
            for bot in bots:
                if str(bot["id"]) == str(BotID):
                    accounts = bot["accounts"]
                    session_name = (
                        requests.form["session_name"]
                        if "session_name" in requests.form
                        else ""
                    )
                    if session_name == "":
                        error = "Please enter session name."
                        break

                    if not session_name.isalnum():
                        error = "Session name can only contain a-z, A-Z, 0-9"
                        break

                    session_name = "ma_" + session_name
                    if session_name in [
                        account["session_name"] for account in accounts
                    ]:
                        error = "Session name already exists."
                        break

                    web_app_url = (
                        requests.form["web_app_url"]
                        if "web_app_url" in requests.form
                        else ""
                    )

                    proxy = requests.form["proxy"] if "proxy" in requests.form else ""
                    user_agent = (
                        requests.form["user_agent"]
                        if "user_agent" in requests.form
                        else ""
                    )

                    account = {
                        "id": hashlib.md5(session_name.encode()).hexdigest(),
                        "session_name": session_name,
                        "display_name": session_name.replace("ma_", ""),
                        "web_app_data": web_app_url,
                        "proxy": proxy,
                        "user_agent": user_agent,
                        "disabled": False,
                    }

                    accounts.append(account)

                    with open(f"modules/{bot['name']}/accounts.json", "w") as f:
                        json.dump(accounts, f, indent=4)

                    bots[bots.index(bot)]["accounts"] = accounts
                    success = (
                        f"Account {account['display_name']} added successfully."
                    )

                    webServer.logger.info(
                        f"{lc.g}➕ Account added, Bot Name: {lc.rs + lc.c + bot['name'] + lc.rs + lc.g}, Session Name: {lc.rs + lc.c + account['display_name'] + lc.rs}"
                    )

        if "edit_account" in requests.form and "account_id" in requests.form:
            AccountID = requests.form["account_id"]
            for bot in bots:
                if str(bot["id"]) == str(requests.form["edit_account"]):
                    accounts = bot["accounts"]
                    for account in accounts:
                        if str(account["id"]) == str(AccountID):
                            account["web_app_data"] = (
                                requests.form["web_app_url"]
                                if "web_app_url" in requests.form
                                else ""
                            )
                            account["proxy"] = (
                                requests.form["proxy"] if "proxy" in requests.form else ""
                            )
                            account["user_agent"] = (
                                requests.form["user_agent"]
                                if "user_agent" in requests.form
                                else ""
                            )

                            with open(f"modules/{bot['name']}/accounts.json", "w") as f:
                                json.dump(accounts, f, indent=4)

                            bots[bots.index(bot)]["accounts"] = accounts
                            success = f"Account {account['display_name']} updated successfully."
                            webServer.logger.info(
                                f"{lc.g}🔄 Account updated, Bot Name: {lc.rs + lc.c + bot['name'] + lc.rs + lc.g}, Session Name: {lc.rs + lc.c + account['display_name'] + lc.rs}"
                            )
                            break

        db.Close()
        return render_template(
            "admin/bots.html", error=error, success=success, bots=bots
        )
