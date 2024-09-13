# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

from flask import redirect, render_template, session

from utils.database import Database
import utils.variables as vr
import utils.Git as Git


class admin:
    def dashboard(self, request, webServer):
        if "admin" not in session:
            return redirect("/auth/login.py")
        Last_Update = "..."
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
                Last_Update = Last_Update
                Update_Available = True
            elif (
                webServer.local_git_commit != None
                and webServer.local_git_commit != webServer.github_git_commit["sha"]
            ):
                Last_Update = Last_Update

        return render_template(
            "admin/dashboard.html",
            Server_IP=webServer.public_ip,
            App_Version=vr.APP_VERSION,
            Last_Update=Last_Update,
            Update_Available=Update_Available,
        )
