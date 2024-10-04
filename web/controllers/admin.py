# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import json
import os
import hashlib
import base64
import re
import signal
from flask import redirect, render_template, session

from mcf_utils.database import Database
import mcf_utils.variables as vr
import mcf_utils.Git as Git
import mcf_utils.logColors as lc
import mcf_utils.api as api
import mcf_utils.utils as utils


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

        commit_hash = mcf_version.get("commit_hash") if mcf_version else None
        commit_date = mcf_version.get("commit_date") if mcf_version else None
        change_logs = mcf_version.get("change_logs") if mcf_version else None

        update_available = commit_hash and not git.GitHasCommit(commit_hash)

        if update_available and "update" in request.args:
            git.UpdateProject(module_threads=webServer.module_threads)
            return "Updating..."

        if update_available and "start_update" in request.args:
            return render_template(
                "admin/updating.html",
                theme=self.theme,
            )

        if "update" in request.args or "start_update" in request.form:
            return redirect("/admin/dashboard.py")

        return render_template(
            "admin/dashboard.html",
            server_ip=webServer.public_ip,
            app_version=vr.APP_VERSION,
            last_update=commit_date,
            update_available=update_available,
            license=license,
            change_logs=change_logs,
            uptime=utils.TimeAgo(webServer.startTime),
            theme=self.theme,
        )

    def restart(self, request, webServer):
        if "admin" not in session:
            return redirect("/auth/login.py")

        if "restart" in request.args:
            webServer.logger.info("<yellow>🔄 Restarting the server...</yellow>")
            webServer.module_threads.stop_all_modules()
            os.kill(os.getpid(), signal.SIGINT)

        return render_template("admin/restarting.html", theme=self.theme)

    def settings(self, request, webServer):
        if "admin" not in session:
            return redirect("/auth/login.py")

        error = None
        success = None

        db = Database("database.db", webServer.logger)
        license = db.getSettings("license", "Free License")

        if request.method == "POST":
            action = request.form.get("action")
            if action == "change_password":
                current_password = request.form.get("current-password")
                new_password = request.form.get("new-password")
                confirm_password = request.form.get("confirm-password")

                if not current_password or not new_password or not confirm_password:
                    error = "Please fill all the fields."
                elif db.getSettings("admin_password") != current_password:
                    error = "Current password is incorrect!"
                elif new_password != confirm_password:
                    error = "New password and confirm password do not match."
                elif len(new_password) < 8:
                    error = "Password should be at least 8 characters long."
                else:
                    db.updateSettings("admin_password", new_password)
                    success = "Password changed successfully."
                    webServer.logger.info(
                        f"<green>🔑 Admin password changed successfully, New password: </green><red>{new_password}</red>"
                    )
            elif action == "change_settings":
                theme = request.form.get("theme")
                if theme:
                    db.updateSettings("theme", theme)
                    self.theme = theme
                    success = "Settings updated successfully."
                    webServer.logger.info(
                        f"<green>🔄 Settings updated, Theme: </green><cyan>{theme}</cyan>"
                    )

        theme_list = [
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
            themeList=theme_list,
        )

    def accounts(self, request, webServer):
        if "admin" not in session:
            return redirect("/auth/login.py")

        accounts = []
        success = None
        error = None

        accounts_file = "telegram_accounts/accounts.json"

        try:
            if os.path.exists(accounts_file):
                with open(accounts_file, "r") as f:
                    accounts = json.load(f)

                if not accounts:
                    error = "No accounts found."
            else:
                error = "No accounts found."
        except Exception as e:
            error = "Error loading accounts..."

        if error:
            return render_template(
                "admin/accounts.html",
                accounts=accounts,
                error=error,
                theme=self.theme,
            )

        file_updated = False
        if "disable" in request.args:
            AccountID = request.args.get("disable")
            for account in accounts:
                if str(account["id"]) == str(AccountID):
                    account["disabled"] = True
                    success = (
                        f"Account {account['session_name']} disabled successfully."
                    )
                    webServer.logger.info(
                        f"<red>🔒 Account disabled, Account ID: </red><cyan>{AccountID}</cyan>"
                    )
                    file_updated = True
                    break
        elif "enable" in request.args:
            AccountID = request.args.get("enable")
            for account in accounts:
                if str(account["id"]) == str(AccountID):
                    account["disabled"] = False
                    success = f"Account {account['session_name']} enabled successfully."
                    webServer.logger.info(
                        f"<green>🔓 Account enabled, Account ID: </green><cyan>{AccountID}</cyan>"
                    )
                    file_updated = True
                    break
        elif "delete" in request.args:
            session_name = request.args.get("delete")
            for account in accounts:
                if account["session_name"] == session_name:
                    accounts.remove(account)
                    success = f"Account {account['session_name']} deleted successfully."
                    webServer.logger.info(
                        f"<red>🗑 Account deleted, Session Name: </red><cyan>{session_name}</cyan>"
                    )
                    file_updated = True
                    try:
                        os.remove(f"telegram_accounts/{session_name}.session")
                    except Exception as e:
                        pass
                    break

        if request.method == "POST" and "account_id" in request.form:
            AccountID = request.form["account_id"]
            for account in accounts:
                if str(account["id"]) == str(AccountID):

                    account["proxy"] = request.form.get("proxy", "")

                    if account["proxy"] != "":
                        if account["proxy"] and account["proxy"][-1] == "/":
                            account["proxy"] = account["proxy"][:-1]

                        self.logger.info(
                            f"<g>🔗 Testing account proxy, Proxy: </g><cyan>{account['proxy']}</cyan>"
                        )
                        proxyTestResponse = utils.testProxy(account["proxy"])
                        if not proxyTestResponse:
                            error = "Proxy is not working."
                            self.logger.info(
                                "<red>└─ ❌ Proxy is not working. It is either invalid or too slow.</red>"
                            )
                            break

                        self.logger.info(
                            f"<green>└─ ✅ Proxy tested successfully, IP: </green><cyan>{utils.HideIP(proxyTestResponse)}</cyan>"
                        )

                    account["user_agent"] = request.form.get("user_agent", "")
                    success = f"Account {account['session_name']} updated successfully."
                    webServer.logger.info(
                        f"<green>🔄 Account updated, Account ID: </green><cyan>{AccountID}</cyan>"
                    )
                    file_updated = True
                    break

        if file_updated:
            try:
                with open(accounts_file, "w") as f:
                    json.dump(accounts, f, indent=4)
            except Exception as e:
                error = f"Error saving accounts..."

        return render_template(
            "admin/accounts.html",
            accounts=accounts,
            error=error,
            success=success,
            theme=self.theme,
        )

    def change_license(self, request, webServer):
        if "admin" not in session:
            return redirect("/auth/login.py")

        db = Database("database.db", webServer.logger)
        license = db.getSettings("license", "Free License")
        apiObj = api.API(webServer.logger)

        error, success, credit, ton_wallet, user_id, devices = (
            None,
            None,
            None,
            None,
            None,
            None,
        )

        if request.method == "POST" and "license" in request.form:
            license_key = request.form["license"]
            response = apiObj.validate_license(license_key)
            if response and "error" not in response and "credit" in response:
                db.updateSettings("license", license_key)
                success = "License updated successfully."
                webServer.logger.info(
                    f"<green>🔑 License updated successfully, New license: </green><cyan>***{license_key[5:15]}***</cyan>"
                )
                webServer.logger.info(
                    f"<green>📖 License Credit: </green><cyan>{str(response['credit'])}$</cyan><green>, IP: </green><cyan>{utils.HideIP(response['ip'])}</cyan>"
                )
                license, credit, ton_wallet, user_id, devices = (
                    license_key,
                    response["credit"],
                    response["ton_wallet"],
                    response["user_id"],
                    response["devices"],
                )
            else:
                error = "Invalid license key."
        else:
            response = apiObj.validate_license(license)
            if response and "error" not in response and "credit" in response:
                credit, ton_wallet, user_id, devices = (
                    response["credit"],
                    response["ton_wallet"],
                    response["user_id"],
                    response["devices"],
                )

        return render_template(
            "admin/change_license.html",
            error=error,
            success=success,
            server_ip=webServer.public_ip,
            license=license,
            credit=credit,
            ton_wallet=ton_wallet,
            user_id=user_id,
            devices=devices,
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
        else:
            server_modules = apiObj.get_modules(license)
            if server_modules is None or "error" in server_modules:
                error = "Unable to get modules, please try again later."
            else:
                installed_ModulesDir = os.listdir("modules")
                installed_Modules = [
                    module
                    for module in installed_ModulesDir
                    if os.path.isdir(f"modules/{module}")
                    and os.path.exists(f"modules/{module}/bot.py")
                ]

                for module in server_modules.get("modules", []):
                    module["commit_date"] = module.get("commit_date", "Unknown")
                    module["installed"] = module["name"] in installed_Modules

                if request.method == "POST" and "install_module" in request.form:
                    moduleID = int(request.form["install_module"])
                    for module in server_modules["modules"]:
                        if int(module["id"]) == moduleID:
                            response = apiObj.install_module(license, moduleID)
                            if (
                                response
                                and response.get("status") == "success"
                                and "name" in response
                                and "download_link" in response
                            ):
                                webServer.logger.info(
                                    f"<green>➕ Installing module, Module Name: <cyan>{module['name']}</cyan></green>"
                                )
                                git = Git.Git(webServer.logger, webServer.config)
                                git.gitClone(
                                    response["download_link"],
                                    f"modules/{response['name']}",
                                )
                                success = "Module installed successfully. Please configure the module and enable it."
                                webServer.logger.info(
                                    f"<green>➕ Module installed, Module Name: <cyan>{module['name']}</cyan></green>"
                                )
                                module["installed"] = True
                                module["owned"] = True
                                db.updateSettings(f"{module['name']}_disabled", True)
                            else:
                                error = response.get(
                                    "error",
                                    "Unable to install module, please try again later.",
                                )
                            break

        return render_template(
            "admin/add_bot.html",
            error=error,
            success=success,
            modules=server_modules.get("modules", []) if not error else [],
            theme=self.theme,
        )

    def bot_logs(self, requests, webServer):
        if "admin" not in session:
            return redirect("/auth/login.py")

        logs = ""
        if requests.method != "POST" or "bot_id" not in requests.args:
            return redirect("/admin/bots.py")

        bot = requests.args.get("bot_id")

        bots = self._bots_load_all(webServer)
        for b in bots:
            if b["id"] == bot:
                logs = b["logs"]
                break

        return {"status": "success", "logs": logs}

    def bots(self, requests, webServer):
        if "admin" not in session:
            return redirect("/auth/login.py")

        error = None
        success = None

        accounts_file = "telegram_accounts/accounts.json"

        pyrogram_accounts = []
        try:
            if os.path.exists(accounts_file):
                with open(accounts_file, "r") as f:
                    pyrogram_accounts = json.load(f)
        except Exception as e:
            pass

        bots = self._bots_load_all(webServer)
        if "disable" in requests.args:
            success = self._bots_disable(requests, bots, webServer)
        elif "enable" in requests.args:
            success = self._bots_enable(requests, bots, webServer)
        elif "delete_account" in requests.args and "bot_id" in requests.args:
            success = self._bots_delete_account(requests, bots, webServer)
        elif "disable_account" in requests.args and "bot_id" in requests.args:
            success = self._bots_disable_account(requests, bots, webServer)
        elif "enable_account" in requests.args and "bot_id" in requests.args:
            success = self._bots_enable_account(requests, bots, webServer)
        elif "stop_bot" in requests.args:
            success = self._bots_stop_bot(requests, bots, webServer)
        elif "start_bot" in requests.args:
            success = self._bots_start_bot(requests, bots, webServer)
        elif "restart_bot" in requests.args:
            success = self._bots_restart_bot(requests, bots, webServer)

        if requests.args:
            bots = self._bots_load_all(webServer)

        if requests.method != "POST":
            return render_template(
                "admin/bots.html",
                error=error,
                success=success,
                bots=bots,
                pyrogram_accounts=pyrogram_accounts,
                theme=self.theme,
            )

        if "bot_id" in requests.form:
            success, error = self._bots_update_settings(requests, bots, webServer)

        if "add_account" in requests.form:
            success, error = self._bots_add_account(requests, bots, webServer)

        if "edit_account" in requests.form and "account_id" in requests.form:
            success, error = self._bots_edit_account(requests, bots, webServer)

        if "disabled_pyrogram_sessions" in requests.form:
            success, error = self._bots_disable_sessions(requests, bots, webServer)

        bots = self._bots_load_all(webServer)

        return render_template(
            "admin/bots.html",
            error=error,
            success=success,
            bots=bots,
            pyrogram_accounts=pyrogram_accounts,
            theme=self.theme,
        )

    def _bots_disable_sessions(self, requests, bots, webServer):
        BotID = requests.form["disabled_pyrogram_sessions"]
        for bot in bots:
            if str(bot["id"]) == str(BotID):
                disabled_sessions = requests.form.getlist("disabled_sessions")
                bot["disabled_sessions"] = disabled_sessions
                with open(f"modules/{bot['name']}/disabled_sessions.json", "w") as f:
                    json.dump(disabled_sessions, f, indent=4)
                webServer.logger.info(
                    f"🔒 <yellow>Module disabled sessions updated</yellow>, Bot Name: <cyan>{bot['name']}</cyan>"
                )
                return "Module disabled sessions updated.", None
        return None, "Bot not found."

    def _bots_load_all(self, webServer):
        modules = os.listdir("modules")
        bots = []
        db = Database("database.db", webServer.logger)
        for module in modules:
            if os.path.isdir(f"modules/{module}") and os.path.exists(
                f"modules/{module}/bot.py"
            ):
                bot = self._bots_load_single(module, db, webServer)
                bots.append(bot)
        return bots

    def _bots_load_single(self, module, db, webServer):
        bot = {"name": module, "id": hashlib.md5(module.encode()).hexdigest()}
        bot["logo"] = self._bots_load_logo(module)
        bot["disabled"] = db.getSettings(f"{module}_disabled", False)
        bot["logs"] = self._bots_load_logs(module)
        bot["settings"] = self._bots_load_json(
            f"modules/{module}/bot_settings.json", {}
        )
        bot["settings_types"] = self._bots_load_json(
            f"modules/{module}/bot_settings_types.json", None
        )
        bot["disabled_sessions"] = self._bots_load_json(
            f"modules/{module}/disabled_sessions.json", []
        )
        bot["disable_accounts_file"] = self._bots_file_exists(
            f"modules/{module}/.disabled_module_accounts"
        )

        bot["accounts"] = self._bots_load_json(f"modules/{module}/accounts.json", [])
        bot["settings_inputs"] = self._bots_prepare_settings_inputs(bot)
        bot["is_running"] = webServer.module_threads.is_module_running(module)
        bot["uptime"] = utils.TimeAgo(
            webServer.module_threads.get_module_start_time(module)
        )
        return bot

    def _bots_load_logo(self, module):
        logo_path = f"modules/{module}/logo.png"
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                logo_data = base64.b64encode(f.read()).decode()
            return f"data:image/png;base64,{logo_data}"
        return ""

    def _bots_load_logs(self, module):
        log_path = f"modules/{module}/bot.log"
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            logs = "".join(lines[-100:])
            logs = utils.ansi_to_html(logs)
            logs = re.sub(r"\[MasterCryptoFarmBot\] ", "", logs)
            return logs
        return "No logs available."

    def _bots_load_json(self, path, default):
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except Exception as e:
                pass
        return default

    def _bots_file_exists(self, path):
        if os.path.exists(path):
            return True
        return False

    def _bots_prepare_settings_inputs(self, bot):
        settings_inputs = {}
        if bot["settings_types"] is None:
            return settings_inputs

        for setting_type in bot["settings_types"]:
            key = setting_type.get("key")
            name = setting_type.get("name")
            type = setting_type.get("type")
            if not key or not name or not type:
                continue

            settings_inputs[key] = {
                "key": key,
                "name": name,
                "type": type,
                "placeholder": setting_type.get("placeholder"),
                "description": setting_type.get("description"),
                "value": bot["settings"].get(
                    key, setting_type.get("default_value", "")
                ),
                "required": setting_type.get("required", False),
                "min": setting_type.get("min"),
                "max": setting_type.get("max"),
                "options": setting_type.get("options"),
                "multi_select": setting_type.get("multi_select", False),
            }

            if type == "select":
                for option in settings_inputs[key]["options"]:
                    option["selected"] = (
                        settings_inputs[key]["value"] == option["value"]
                        if not settings_inputs[key]["multi_select"]
                        else option["value"] in settings_inputs[key]["value"]
                    )

        return settings_inputs

    def _bots_disable(self, requests, bots, webServer):
        BotID = requests.args.get("disable", 0)
        for bot in bots:
            if str(bot["id"]) == str(BotID):
                db = Database("database.db", webServer.logger)
                db.updateSettings(f"{bot['name']}_disabled", True)
                bot["disabled"] = True
                webServer.logger.info(
                    f"<red>🔒 Bot disabled, Bot Name: <cyan>{bot['name']}</cyan></red>"
                )
                webServer.module_threads.stop_module(bot["name"])
                return f"Bot {bot['name']} disabled successfully."
        return None

    def _bots_enable(self, requests, bots, webServer):
        BotID = requests.args.get("enable", 0)
        for bot in bots:
            if str(bot["id"]) == str(BotID):
                db = Database("database.db", webServer.logger)
                db.deleteSettings(f"{bot['name']}_disabled")
                bot["disabled"] = False
                webServer.logger.info(
                    f"<green>🔓 Bot enabled, Bot Name: <cyan>{bot['name']}</cyan></green>"
                )

                webServer.module_threads.run_module(bot["name"])
                return f"Bot {bot['name']} enabled successfully."
        return None

    def _bots_delete_account(self, requests, bots, webServer):
        BotID = requests.args.get("bot_id", 0)
        AccountID = requests.args.get("delete_account", 0)
        for bot in bots:
            if str(bot["id"]) == str(BotID):
                accounts = bot["accounts"]
                for account in accounts:
                    if str(account["id"]) == str(AccountID):
                        accounts.remove(account)
                        self._bots_save_accounts(bot["name"], accounts)
                        bot["accounts"] = accounts
                        webServer.logger.info(
                            f"<red>🗑 Account deleted, Bot Name: <cyan>{bot['name']}</cyan>, Session Name: <cyan>{account['display_name']}</cyan></red>"
                        )
                        return (
                            f"Account {account['display_name']} deleted successfully."
                        )
        return None

    def _bots_disable_account(self, requests, bots, webServer):
        BotID = requests.args.get("bot_id", 0)
        AccountID = requests.args.get("disable_account", 0)
        for bot in bots:
            if str(bot["id"]) == str(BotID):
                accounts = bot["accounts"]
                for account in accounts:
                    if str(account["id"]) == str(AccountID):
                        account["disabled"] = True
                        self._bots_save_accounts(bot["name"], accounts)
                        bot["accounts"] = accounts
                        webServer.logger.info(
                            f"<red>🔒 Account disabled, Bot Name: <cyan>{bot['name']}</cyan>, Session Name: <cyan>{account['display_name']}</cyan></red>"
                        )
                        return (
                            f"Account {account['display_name']} disabled successfully."
                        )
        return None

    def _bots_enable_account(self, requests, bots, webServer):
        BotID = requests.args.get("bot_id", 0)
        AccountID = requests.args.get("enable_account", 0)
        for bot in bots:
            if str(bot["id"]) == str(BotID):
                accounts = bot["accounts"]
                for account in accounts:
                    if str(account["id"]) == str(AccountID):
                        account["disabled"] = False
                        self._bots_save_accounts(bot["name"], accounts)
                        bot["accounts"] = accounts
                        webServer.logger.info(
                            f"<green>🔓 Account enabled, Bot Name: <cyan>{bot['name']}</cyan>, Session Name: <cyan>{account['display_name']}</cyan></green>"
                        )
                        return (
                            f"Account {account['display_name']} enabled successfully."
                        )
        return None

    def _bots_stop_bot(self, requests, bots, webServer):
        BotID = requests.args.get("stop_bot", 0)
        for bot in bots:
            if str(bot["id"]) == str(BotID):
                webServer.module_threads.stop_module(bot["name"], True)
                webServer.logger.info(
                    f"<red>🛑 Bot module stopped, Bot Module Name: <cyan>{bot['name']}</cyan></red>"
                )
                return f"Bot {bot['name']} stopped successfully."
        return None

    def _bots_start_bot(self, requests, bots, webServer):
        BotID = requests.args.get("start_bot", 0)
        for bot in bots:
            if str(bot["id"]) == str(BotID):
                webServer.module_threads.run_module(bot["name"], True)
                webServer.logger.info(
                    f"<green>▶ Bot module started, Bot Module Name: <cyan>{bot['name']}</cyan></green>"
                )
                return f"Bot {bot['name']} started successfully."
        return None

    def _bots_restart_bot(self, requests, bots, webServer):
        BotID = requests.args.get("restart_bot", 0)
        for bot in bots:
            if str(bot["id"]) == str(BotID):
                webServer.module_threads.restart_module(bot["name"])
                webServer.logger.info(
                    f"<green>🔄 Bot module restarted, Bot Module Name: <cyan>{bot['name']}</cyan></green>"
                )
                return f"Bot {bot['name']} restarted successfully."
        return None

    def _bots_save_accounts(self, bot_name, accounts):
        with open(f"modules/{bot_name}/accounts.json", "w") as f:
            json.dump(accounts, f, indent=4)

    def _bots_update_settings(self, requests, bots, webServer):
        BotID = requests.form["bot_id"]
        for bot in bots:
            if str(bot["id"]) == str(BotID):
                settings = bot["settings"]
                settings_inputs = bot["settings_inputs"]
                error = self._bots_validate_settings(requests, settings_inputs)
                if error:
                    return None, error

                for key in settings_inputs:
                    settings[key] = self._bots_get_setting_value(
                        requests, key, settings_inputs[key]
                    )

                self._bots_save_settings(bot["name"], settings)
                bot["settings"] = settings
                webServer.logger.info(
                    f"<green>🔄 Bot settings updated, Bot Name: <cyan>{bot['name']}</cyan></green>"
                )

                webServer.module_threads.restart_module(bot["name"])
                return f"Settings updated successfully.", None
        return None, "Bot not found."

    def _bots_validate_settings(self, requests, settings_inputs):
        for key in settings_inputs:
            if key not in requests.form and settings_inputs[key].get("required"):
                return "Please fill all the fields."
            if settings_inputs[key]["type"] in ["number", "range"]:
                try:
                    int(requests.form[key])
                except (ValueError, KeyError):
                    return f"{settings_inputs[key]['name']} should be a number."
        return None

    def _bots_get_setting_value(self, requests, key, setting_input):
        if key not in requests.form:
            if setting_input["type"] == "checkbox":
                return False
            if setting_input["type"] == "select":
                return (
                    setting_input["options"][0]["value"]
                    if not setting_input["multi_select"]
                    else []
                )
            if setting_input["type"] in ["number", "range"]:
                return setting_input.get("min", 0)
            return ""
        if setting_input["type"] in ["number", "range"]:
            return int(requests.form[key])
        if setting_input["type"] == "checkbox":
            return True
        if setting_input["type"] == "select":
            return (
                requests.form.getlist(key)
                if setting_input["multi_select"]
                else requests.form[key]
            )
        return requests.form[key]

    def _bots_save_settings(self, bot_name, settings):
        with open(f"modules/{bot_name}/bot_settings.json", "w") as f:
            json.dump(settings, f, indent=4)

    def _bots_add_account(self, requests, bots, webServer):
        BotID = requests.form["add_account"]
        for bot in bots:
            if str(bot["id"]) == str(BotID):
                if bot["disable_accounts_file"]:
                    return None, "You cannot add more accounts to this bot."

                session_name = requests.form.get("session_name", "")
                if not session_name:
                    return None, "Please enter session name."
                if not session_name.isalnum():
                    return None, "Session name can only contain a-z, A-Z, 0-9"

                session_name = "ma_" + session_name
                if session_name in [
                    account["session_name"] for account in bot["accounts"]
                ]:
                    return None, "Session name already exists."

                account = {
                    "id": hashlib.md5(session_name.encode()).hexdigest(),
                    "session_name": session_name,
                    "display_name": session_name.replace("ma_", ""),
                    "web_app_data": requests.form.get("web_app_url", ""),
                    "proxy": requests.form.get("proxy", ""),
                    "user_agent": requests.form.get("user_agent", ""),
                    "disabled": False,
                }

                if account["proxy"] != "":
                    if account["proxy"][-1] == "/":
                        account["proxy"] = account["proxy"][:-1]

                    webServer.logger.info(
                        f"<g>🔗 Testing account proxy, Proxy: </g><cyan>{account['proxy']}</cyan>"
                    )

                    proxyTestResponse = utils.testProxy(account["proxy"])
                    if not proxyTestResponse:
                        webServer.logger.info(
                            "<red>└─ ❌ Proxy is not working. It is either invalid or too slow.</red>"
                        )
                        return None, "Proxy is not working."
                    webServer.logger.info(
                        f"<green>└─ ✅ Proxy tested successfully, IP: </green><cyan>{utils.HideIP(proxyTestResponse)}</cyan>"
                    )

                bot["accounts"].append(account)
                self._bots_save_accounts(bot["name"], bot["accounts"])
                webServer.logger.info(
                    f"<green>➕ Account added, Bot Name: <cyan>{bot['name']}</cyan>, Session Name: <cyan>{account['display_name']}</cyan></green>"
                )
                return f"Account {account['display_name']} added successfully.", None
        return None, "Bot not found."

    def _bots_edit_account(self, requests, bots, webServer):
        AccountID = requests.form["account_id"]
        for bot in bots:
            if str(bot["id"]) == str(requests.form["edit_account"]):
                for account in bot["accounts"]:
                    if str(account["id"]) == str(AccountID):
                        account["web_app_data"] = requests.form.get("web_app_url", "")
                        account["proxy"] = requests.form.get("proxy", "")
                        account["user_agent"] = requests.form.get("user_agent", "")

                        if account["proxy"] != "":
                            if account["proxy"][-1] == "/":
                                account["proxy"] = account["proxy"][:-1]

                            webServer.logger.info(
                                f"<g>🔗 Testing account proxy, Proxy: </g><cyan>{account['proxy']}</cyan>"
                            )

                            proxyTestResponse = utils.testProxy(account["proxy"])
                            if not proxyTestResponse:
                                webServer.logger.info(
                                    "<red>└─ ❌ Proxy is not working. It is either invalid or too slow.</red>"
                                )
                                return None, "Proxy is not working."
                            webServer.logger.info(
                                f"<green>└─ ✅ Proxy tested successfully, IP: </green><cyan>{utils.HideIP(proxyTestResponse)}</cyan>"
                            )

                        self._bots_save_accounts(bot["name"], bot["accounts"])
                        webServer.logger.info(
                            f"<green>🔄 Account updated, Bot Name: <cyan>{bot['name']}</cyan>, Session Name: <cyan>{account['display_name']}</cyan></green>"
                        )
                        return (
                            f"Account {account['display_name']} updated successfully.",
                            None,
                        )
        return None, "Account not found."
