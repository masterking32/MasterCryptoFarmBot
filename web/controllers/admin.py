# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import json
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
                    webServer.logger.info(f"{lc.g}🔑 Admin password changed successfully, New password: {lc.rs + lc.c + request.form["new-password"] + lc.rs}")
                else:
                    error = "New password and confirm password does not match."

            else:
                error = "Please fill all the fields."

        db.Close()
        return render_template("admin/settings.html", error=error, success=success, server_ip=webServer.public_ip, license=license)

    def accounts(self, request, webServer):
        if "admin" not in session:
            return redirect("/auth/login.py")

        accounts = []
        with open("telegram_accounts/accounts.json", "r") as f:
            accounts = json.load(f)

        if "disable" in request.args:
            AccountID = request.args.get("disable", 0)
            for account in accounts:
                if str(account["id"]) == str(AccountID):
                    accounts.remove(account)
                    account["disabled"] = True
                    webServer.logger.info(f"{lc.r}🔒 Account disabled, Account ID: {lc.rs + lc.c + AccountID + lc.rs}")
                    accounts.append(account)
                    break

            with open("telegram_accounts/accounts.json", "w") as f:
                json.dump(accounts, f, indent=4)

        if "enable" in request.args:
            AccountID = request.args.get("enable", 0)
            for account in accounts:
                if str(account["id"]) == str(AccountID):
                    accounts.remove(account)
                    webServer.logger.info(f"{lc.g}🔓 Account enabled, Account ID: {lc.rs + lc.c + AccountID + lc.rs}")
                    account["disabled"] = False
                    accounts.append(account)
                    break

            with open("telegram_accounts/accounts.json", "w") as f:
                json.dump(accounts, f, indent=4)

        return render_template("admin/accounts.html", accounts=accounts)

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
                webServer.logger.info(f"{lc.g}🔑 License updated successfully, New license: {lc.rs + lc.c + license + lc.rs}")
                webServer.logger.info(f"{lc.g}📖 License Credit: {lc.rs + lc.c + str(response["credit"]) + "$" + lc.rs + lc.g}, IP: {lc.rs + lc.c + response["ip"] + lc.rs}")
                license = license_key
                credit = response["credit"]
            else:
                error = "Invalid license key."
        db.Close()
        return render_template("admin/change_license.html", error=error, success=success, server_ip=webServer.public_ip, license=license, credit=credit)
