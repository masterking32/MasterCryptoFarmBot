# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

from flask import redirect, render_template, session

from utils.database import Database
import utils.variables as vr
import utils.Git as Git
import utils.logColors as lc


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
