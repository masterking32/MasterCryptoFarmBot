from flask import redirect, render_template, session

from utils.database import Database


class auth:
    def login(self, request, webServer):
        db = Database("database.db", webServer.logger)
        if "admin" in session:
            return redirect("/admin/dashboard.py")

        print(session)
        if request.method == "POST":
            if "password" in request.form:
                password = request.form["password"]
                adminPassword = db.getSettings("admin_password", "admin")
                db.Close()
                if password == adminPassword:
                    session["admin"] = True
                    return redirect("/admin/dashboard.py")
                else:
                    return render_template("auth/login.html", error="Invalid password")

        return render_template("auth/login.html")
