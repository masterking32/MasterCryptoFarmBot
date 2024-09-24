# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import json
import os
import hashlib
import base64
import re
from flask import redirect, render_template, session

from utils.database import Database
import utils.variables as vr
import utils.Git as Git
import utils.logColors as lc
import utils.api as api
import utils.utils as utils


class admin:
    def __init__(self, logger):
        self.logger = logger
        self.theme = "night"
        db = Database("database.db", self.logger)
        self.theme = db.getSettings("theme", "night")

    def dashboard(self, request, webServer):
        if "admin" not in session:
            return redirect("/auth/login.py")

        db = Database("database.db", webServer.logger)
        license = db.getSettings("license", "Free License")
        git = Git.Git(webServer.logger, webServer.config)
        apiObj = api.API(webServer.logger)
        mcf_version = apiObj.get_mcf_version()
        commit_hash = (
            None
            if mcf_version is None or "commit_hash" not in mcf_version
            else mcf_version["commit_hash"]
        )
        commit_date = (
            None
            if mcf_version is None or "commit_date" not in mcf_version
            else mcf_version["commit_date"]
        )

        Update_Available = False
        if commit_hash is not None and not git.GitHasCommit(commit_hash):
            Update_Available = True

        if Update_Available and "update" in request.args:
            git.UpdateProject()
            return redirect("/admin/dashboard.py")

        if "update" in request.args:
            return redirect("/admin/dashboard.py")

        return render_template(
            "admin/dashboard.html",
            Server_IP=webServer.public_ip,
            App_Version=vr.APP_VERSION,
            Last_Update=commit_date,
            Update_Available=Update_Available,
            License=license,
            theme=self.theme,
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
                        f"<green>🔑 Admin password changed successfully, New password: </green><red>{request.form['new-password']}</red>"
                    )
                else:
                    error = "New password and confirm password does not match."

            else:
                error = "Please fill all the fields."
        elif request.method == "POST" and "change_settings" in request.form:
            if "theme" in request.form:
                db.updateSettings("theme", request.form["theme"])
                self.theme = request.form["theme"]
                success = "Settings updated successfully."
                webServer.logger.info(
                    f"<green>🔄 Settings updated, Theme: </green><cyan>{request.form['theme']}</cyan>"
                )

        themeList = [
            "night",
            "light",
            "dark",
            "cupcake",
            "bumblebee",
            "emerald",
            "corporate",
            "synthwave",
            "retro",
            "cyberpunk",
            "Valentine",
            "halloween",
            "garden",
            "forest",
            "aqua",
            "lofi",
            "pastel",
            "fantasy",
            "wireframe",
            "black",
            "luxury",
            "dracula",
            "cmyk",
            "autumn",
            "business",
            "acid",
            "lemonade",
            "coffee",
            "winter",
            "dim",
            "nord",
            "sunset",
        ]
        return render_template(
            "admin/settings.html",
            error=error,
            success=success,
            server_ip=webServer.public_ip,
            license=license,
            theme=self.theme,
            themeList=themeList,
        )

    def accounts(self, request, webServer):
        if "admin" not in session:
            return redirect("/auth/login.py")

        accounts = []
        success = ""
        error = ""
        try:
            if os.path.exists("telegram_accounts/accounts.json"):
                with open("telegram_accounts/accounts.json", "r") as f:
                    accounts = json.load(f)
                    f.close()
            else:
                error = "No accounts found."
        except:
            pass

        if "disable" in request.args:
            AccountID = request.args.get("disable", 0)
            for account in accounts:
                if str(account["id"]) == str(AccountID):
                    success = (
                        f"Account {account['session_name']} disabled successfully."
                    )
                    account["disabled"] = True
                    webServer.logger.info(
                        f"<red>🔒 Account disabled, Account ID: </red><cyan>{AccountID}</cyan>"
                    )
                    break

            with open("telegram_accounts/accounts.json", "w") as f:
                json.dump(accounts, f, indent=4)
                f.close()

        if "enable" in request.args:
            AccountID = request.args.get("enable", 0)
            for account in accounts:
                if str(account["id"]) == str(AccountID):
                    success = f"Account {account['session_name']} enabled successfully."
                    webServer.logger.info(
                        f"<green>🔓 Account enabled, Account ID: </green><cyan>{AccountID}</cyan>"
                    )
                    account["disabled"] = False
                    break

            with open("telegram_accounts/accounts.json", "w") as f:
                json.dump(accounts, f, indent=4)
                f.close()

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
                        f"<green>🔄 Account updated, Account ID: </green><cyan>{AccountID}</cyan>"
                    )
                    break

            with open("telegram_accounts/accounts.json", "w") as f:
                json.dump(accounts, f, indent=4)
                f.close()

        return render_template(
            "admin/accounts.html",
            accounts=accounts,
            SystemOS=webServer.SystemOS,
            error=error,
            success=success,
            theme=self.theme,
        )

    def change_license(self, request, webServer):
        if "admin" not in session:
            return redirect("/auth/login.py")

        error = None
        success = None

        db = Database("database.db", webServer.logger)
        license = db.getSettings("license", "Free License")
        credit = None
        ton_wallet = None
        user_id = None
        apiObj = api.API(webServer.logger)

        if request.method == "POST" and "license" in request.form:
            license_key = request.form["license"]
            response = apiObj.validate_license(license_key)
            if response != None and "error" not in response and "credit" in response:
                db.updateSettings("license", license_key)
                success = "License updated successfully."
                webServer.logger.info(
                    f"<green>🔑 License updated successfully, New license: </green><cyan>{license_key[5:15]}</cyan>"
                )
                webServer.logger.info(
                    f"<green>📖 License Credit: </green><cyan>{str(response['credit'])}$</cyan><green>, IP: </green><cyan>{utils.HideIP(response['ip'])}</cyan>"
                )
                license = license_key
                credit = response["credit"]
                ton_wallet = response["ton_wallet"]
                user_id = response["user_id"]
            else:
                error = "Invalid license key."
        else:
            response = apiObj.validate_license(license)
            if response != None and "error" not in response and "credit" in response:
                credit = response["credit"]
                ton_wallet = response["ton_wallet"]
                user_id = response["user_id"]
        return render_template(
            "admin/change_license.html",
            error=error,
            success=success,
            server_ip=webServer.public_ip,
            license=license,
            credit=credit,
            ton_wallet=ton_wallet,
            user_id=user_id,
            theme=self.theme,
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
                        f.close()
                    bot["logo"] = f"data:image/png;base64,{logo_data}"
                else:
                    bot["logo"] = ""

                bot["disabled"] = db.getSettings(f"{module}_disabled", False)

                bot["logs"] = "No logs available."
                if os.path.exists(f"modules/{module}/bot.log"):
                    with open(f"modules/{module}/bot.log", "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        f.close()
                        bot["logs"] = "".join(lines[-100:])
                        bot["logs"] = utils.ansi_to_html(bot["logs"])
                        bot["logs"] = re.sub(
                            r"\[MasterCryptoFarmBot\] \[(.*?)\] \[(.*?)\]",
                            "",
                            bot["logs"],
                        )

                if os.path.exists(f"modules/{module}/bot_settings.json"):
                    with open(f"modules/{module}/bot_settings.json", "r") as f:
                        bot_settings = json.load(f)
                        bot["settings"] = bot_settings
                        f.close()
                else:
                    bot["settings"] = {}

                if os.path.exists(f"modules/{module}/bot_settings_types.json"):
                    with open(f"modules/{module}/bot_settings_types.json", "r") as f:
                        bot_settings = json.load(f)
                        bot["settings_types"] = bot_settings
                        f.close()
                else:
                    bot["settings_types"] = None

                accounts = []
                try:
                    if os.path.exists(f"modules/{module}/accounts.json"):
                        with open(f"modules/{module}/accounts.json", "r") as f:
                            accounts = json.load(f)
                            f.close()
                except:
                    pass

                bot["accounts"] = accounts

                bot["settings_inputs"] = {}
                if bot["settings_types"] is None:
                    bots.append(bot)
                    continue

                for bot_setting_type in bot["settings_types"]:
                    if (
                        "key" not in bot_setting_type
                        or "name" not in bot_setting_type
                        or "type" not in bot_setting_type
                    ):
                        continue

                    key = bot_setting_type["key"]
                    name = bot_setting_type["name"]
                    type = bot_setting_type["type"]
                    placeholder = (
                        None
                        if "placeholder" not in bot_setting_type
                        else bot_setting_type["placeholder"]
                    )
                    description = (
                        None
                        if "description" not in bot_setting_type
                        else bot_setting_type["description"]
                    )
                    min_value = (
                        None
                        if "min" not in bot_setting_type
                        else bot_setting_type["min"]
                    )
                    max_value = (
                        None
                        if "max" not in bot_setting_type
                        else bot_setting_type["max"]
                    )
                    options = (
                        None
                        if "options" not in bot_setting_type
                        else bot_setting_type["options"]
                    )
                    default_value = (
                        None
                        if "default_value" not in bot_setting_type
                        else bot_setting_type["default_value"]
                    )

                    multi_select = (
                        False
                        if "multi_select" not in bot_setting_type
                        else bot_setting_type["multi_select"]
                    )

                    required = (
                        False
                        if "required" not in bot_setting_type
                        else bot_setting_type["required"]
                    )

                    if type == "text":
                        bot["settings_inputs"][key] = {
                            "key": key,
                            "name": name,
                            "type": "text",
                            "placeholder": placeholder,
                            "description": description,
                            "value": (
                                bot["settings"][key]
                                if key in bot["settings"]
                                else (
                                    default_value if default_value is not None else ""
                                )
                            ),
                            "required": required,
                        }
                    elif type == "number":
                        bot["settings_inputs"][key] = {
                            "key": key,
                            "name": name,
                            "type": "number",
                            "placeholder": placeholder,
                            "description": description,
                            "value": (
                                bot["settings"][key]
                                if key in bot["settings"]
                                else (default_value if default_value is not None else 0)
                            ),
                            "min": min_value,
                            "max": max_value,
                            "required": required,
                        }
                    elif type == "checkbox":
                        bot["settings_inputs"][key] = {
                            "key": key,
                            "name": name,
                            "type": "checkbox",
                            "description": description,
                            "value": (
                                bot["settings"][key]
                                if key in bot["settings"]
                                else (
                                    default_value
                                    if default_value is not None
                                    else False
                                )
                            ),
                        }
                    elif type == "select":
                        bot["settings_inputs"][key] = {
                            "key": key,
                            "name": name,
                            "type": "select",
                            "description": description,
                            "value": (
                                bot["settings"][key]
                                if key in bot["settings"]
                                else (
                                    default_value if default_value is not None else ""
                                )
                            ),
                            "options": options,
                            "multi_select": multi_select,
                            "required": required,
                        }

                        for option in options:
                            if not bot["settings_inputs"][key]["multi_select"]:
                                if (
                                    bot["settings_inputs"][key]["value"]
                                    == option["value"]
                                ):
                                    option["selected"] = True
                                else:
                                    option["selected"] = False
                            else:
                                if (
                                    bot["settings_inputs"][key]["value"]
                                    and option["value"]
                                    in bot["settings_inputs"][key]["value"]
                                ):
                                    option["selected"] = True
                                else:
                                    option["selected"] = False

                    elif type == "range":
                        bot["settings_inputs"][key] = {
                            "key": key,
                            "name": name,
                            "type": "range",
                            "description": description,
                            "value": (
                                bot["settings"][key]
                                if key in bot["settings"]
                                else (default_value if default_value is not None else 0)
                            ),
                            "min": min_value,
                            "max": max_value,
                        }

                bots.append(bot)

        if "disable" in requests.args:
            BotID = requests.args.get("disable", 0)
            for bot in bots:
                if str(bot["id"]) == str(BotID):
                    success = f"Bot {bot['name']} disabled successfully."
                    db.updateSettings(f"{bot['name']}_disabled", True)
                    bots[bots.index(bot)]["disabled"] = True
                    webServer.logger.info(
                        f"<red>🔒 Bot disabled, Bot Name: <cyan>{bot['name']}</cyan></red>"
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
                        f"<green>🔓 Bot enabled, Bot Name: <cyan>{bot['name']}</cyan></green>"
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
                            success = f"Account {account['display_name']} deleted successfully."
                            accounts.remove(account)
                            with open(f"modules/{bot['name']}/accounts.json", "w") as f:
                                json.dump(accounts, f, indent=4)
                                f.close()
                            bots[bots.index(bot)]["accounts"] = accounts
                            webServer.logger.info(
                                f"<red>🗑 Account deleted, Bot Name: <cyan>{bot['name']}</cyan>, Session Name: <cyan>{account['display_name']}</cyan></red>"
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
                            success = f"Account {account['display_name']} disabled successfully."
                            account["disabled"] = True
                            with open(f"modules/{bot['name']}/accounts.json", "w") as f:
                                json.dump(accounts, f, indent=4)
                                f.close()
                            bots[bots.index(bot)]["accounts"] = accounts
                            webServer.logger.info(
                                f"<red>🔒 Account disabled, Bot Name: <cyan>{bot['name']}</cyan>, Session Name: <cyan>{account['display_name']}</cyan></red>"
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
                            success = f"Account {account['display_name']} enabled successfully."
                            account["disabled"] = False
                            with open(f"modules/{bot['name']}/accounts.json", "w") as f:
                                json.dump(accounts, f, indent=4)
                                f.close()
                            bots[bots.index(bot)]["accounts"] = accounts
                            webServer.logger.info(
                                f"<green>🔓 Account enabled, Bot Name: <cyan>{bot['name']}</cyan>, Session Name: <cyan>{account['display_name']}</cyan></green>"
                            )

        if requests.method != "POST":
            return render_template(
                "admin/bots.html",
                error=error,
                success=success,
                bots=bots,
                theme=self.theme,
            )

        if "bot_id" in requests.form:
            BotID = requests.form["bot_id"]
            settings = {}
            for bot in bots:
                if str(bot["id"]) == str(BotID):
                    settings = bot["settings"]
                    settings_types = bot["settings_types"]
                    settings_inputs = bot["settings_inputs"]
                    if settings_inputs is None:
                        error = "Bot does not have any settings."
                        break

                    for key in settings_inputs:
                        if (
                            key not in requests.form
                            and "required" in settings_inputs[key]
                            and settings_inputs[key]["required"]
                        ):
                            error = "Please fill all the fields."
                            break

                        if key not in requests.form:
                            if settings_inputs[key]["type"] == "checkbox":
                                settings[key] = False
                            elif settings_inputs[key]["type"] == "select":
                                settings[key] = (
                                    settings_inputs[key]["options"][0]["value"]
                                    if not settings_inputs[key]["multi_select"]
                                    else []
                                )
                            elif settings_inputs[key]["type"] == "number":
                                settings[key] = 0
                            elif settings_inputs[key]["type"] == "range":
                                settings[key] = settings_inputs[key]["min"]
                            else:
                                settings[key] = ""
                        elif (
                            settings_inputs[key]["type"] == "number"
                            or settings_inputs[key]["type"] == "range"
                        ):
                            try:
                                settings[key] = int(requests.form[key])
                            except:
                                error = f"{settings_inputs[key]['name']} should be a number."
                                break
                        elif settings_inputs[key]["type"] == "checkbox":
                            settings[key] = True if key in requests.form else False
                        elif settings_inputs[key]["type"] == "select":
                            if settings_inputs[key]["multi_select"]:
                                settings[key] = requests.form.getlist(key)
                            else:
                                settings[key] = requests.form[key]
                        else:
                            settings[key] = requests.form[key]

                        settings_inputs[key]["value"] = settings[key]
                        if settings_inputs[key]["type"] == "select":
                            for option in settings_inputs[key]["options"]:
                                if not settings_inputs[key]["multi_select"]:
                                    option["selected"] = (
                                        settings[key] == option["value"]
                                    )
                                else:
                                    option["selected"] = (
                                        settings[key]
                                        and option["value"] in settings[key]
                                    )

                    if error is None:
                        with open(f"modules/{bot['name']}/bot_settings.json", "w") as f:
                            json.dump(settings, f, indent=4)
                            f.close()

                        bots[bots.index(bot)]["settings"] = settings
                        success = f"Settings updated successfully."
                        webServer.logger.info(
                            f"<green>🔄 Bot settings updated, Bot Name: <cyan>{bot['name']}</cyan></green>"
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
                        f.close()

                    bots[bots.index(bot)]["accounts"] = accounts
                    success = f"Account {account['display_name']} added successfully."

                    webServer.logger.info(
                        f"<green>➕ Account added, Bot Name: <cyan>{bot['name']}</cyan>, Session Name: <cyan>{account['display_name']}</cyan></green>"
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
                                requests.form["proxy"]
                                if "proxy" in requests.form
                                else ""
                            )
                            account["user_agent"] = (
                                requests.form["user_agent"]
                                if "user_agent" in requests.form
                                else ""
                            )

                            with open(f"modules/{bot['name']}/accounts.json", "w") as f:
                                json.dump(accounts, f, indent=4)
                                f.close()

                            bots[bots.index(bot)]["accounts"] = accounts
                            success = f"Account {account['display_name']} updated successfully."
                            webServer.logger.info(
                                f"<green>🔄 Account updated, Bot Name: <cyan>{bot['name']}</cyan>, Session Name: <cyan>{account['display_name']}</cyan></green>"
                            )
                            break

        return render_template(
            "admin/bots.html",
            error=error,
            success=success,
            bots=bots,
            theme=self.theme,
        )

    def add_bot(self, request, webServer):
        if "admin" not in session:
            return redirect("/auth/login.py")

        error = None
        success = None

        apiObj = api.API(webServer.logger)
        db = Database("database.db", webServer.logger)
        license = db.getSettings("license", "Free License")

        if license == "Free License":
            error = "Please change your license to add bot."
            return render_template(
                "admin/add_bot.html",
                error=error,
                success=success,
                modules=[],
                theme=self.theme,
            )
        server_modules = apiObj.get_modules(license)
        if server_modules is None or "error" in server_modules:
            error = "Unable to get modules, please try again later."
            return render_template(
                "admin/add_bot.html",
                error=error,
                success=success,
                modules=[],
                theme=self.theme,
            )
        elif "error" in server_modules:
            error = server_modules["error"]
            return render_template(
                "admin/add_bot.html",
                error=error,
                success=success,
                modules=[],
                theme=self.theme,
            )

        installed_ModulesDir = os.listdir("modules")
        installed_Modules = []
        for module in installed_ModulesDir:
            if os.path.isdir(f"modules/{module}") and os.path.exists(
                f"modules/{module}/bot.py"
            ):
                installed_Modules.append(module)

        for module in server_modules["modules"]:
            if "commit_date" in module and module["commit_date"] is not None:
                module["commit_date"] = module["commit_date"]
            else:
                module["commit_date"] = "Unknown"

            if module["name"] in installed_Modules:
                server_modules["modules"][server_modules["modules"].index(module)][
                    "installed"
                ] = True
            else:
                server_modules["modules"][server_modules["modules"].index(module)][
                    "installed"
                ] = False

        if request.method == "POST" and "install_module" in request.form:
            moduleID = int(request.form["install_module"])
            for module in server_modules["modules"]:
                if int(module["id"]) == moduleID:
                    response = apiObj.install_module(license, moduleID)
                    if response is None or "error" in response:
                        error = response["error"]
                        break

                    if (
                        response["status"] != "success"
                        or "name" not in response
                        or "download_link" not in response
                    ):
                        error = "Unable to install module, please try again later."
                        break

                    webServer.logger.info(
                        f"<green>➕ Installing module, Module Name: <cyan>{module['name']}</cyan></green>"
                    )

                    # Clone the module inside modules directory
                    git = Git.Git(webServer.logger, webServer.config)
                    response = git.gitClone(
                        response["download_link"], f"modules/{response['name']}"
                    )

                    success = "Module installed successfully. Please configure the module and enable it."

                    webServer.logger.info(
                        f"<green>➕ Module installed, Module Name: <cyan>{module['name']}</cyan></green>"
                    )

                    server_modules["modules"][server_modules["modules"].index(module)][
                        "installed"
                    ] = True
                    server_modules["modules"][server_modules["modules"].index(module)][
                        "owned"
                    ] = True
                    db = Database("database.db", webServer.logger)
                    db.updateSettings(f"{module['name']}_disabled", True)
                    break

        return render_template(
            "admin/add_bot.html",
            error=error,
            success=success,
            modules=server_modules["modules"],
            theme=self.theme,
        )
