# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

from flask import redirect, render_template, session

from utils.database import Database


class admin:
    def dashboard(self, request, webServer):
        if "admin" not in session:
            return redirect("/auth/login.py")

        return render_template("admin/dashboard.html", rerender=True)
