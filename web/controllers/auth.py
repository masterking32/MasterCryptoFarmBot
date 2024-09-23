# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

from flask import redirect, render_template, session

from utils.database import Database


class auth:
    def __init__(self, logger):
        self.logger = logger
        self.theme = "night"
        db = Database("database.db", self.logger)
        self.theme = db.getSettings("theme", "night")
        db.Close()

    def login(self, request, webServer):
        db = Database("database.db", webServer.logger)
        if "admin" in session:
            return redirect("/admin/dashboard.py")

        if request.method == "POST":
            if "password" in request.form:
                password = request.form["password"]
                adminPassword = db.getSettings("admin_password", "admin")
                db.Close()
                if password == adminPassword:
                    session["admin"] = True
                    return redirect("/admin/dashboard.py")
                else:
                    return render_template(
                        "auth/login.html", error="Invalid password", theme=self.theme
                    )

        return render_template("auth/login.html", theme=self.theme)

    def logout(self, request, webServer):
        if "admin" in session:
            session.pop("admin")
        return redirect("/auth/login.py")
