# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import os
import random
import signal
import string
from flask import Flask, render_template, request
import requests

import flask.cli

from utils.database import Database
import utils.logColors as lc
import utils.variables as vr
import logging
import utils.utils as utils


class WebServer:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.host = self.config["web_server"]["host"]
        self.port = self.config["web_server"]["port"]
        self.server = None
        self.public_ip = "127.0.0.1"
        self.SystemOS = os.name

    def LoadFile(self, file):
        try:
            with open(file, "r") as f:
                file_content = f.read()
                f.close()
                return file_content
        except FileNotFoundError:
            return "404 Not Found"

    def GetPublicHTMLPath(self, path):
        current_Dir = os.path.dirname(__file__)
        file_dir = os.path.abspath(
            os.path.join(current_Dir, "../web/public_html/" + path)
        )
        return file_dir

    def GetControllersPath(self, path):
        current_Dir = os.path.dirname(__file__)
        file_dir = os.path.abspath(
            os.path.join(current_Dir, "../web/controllers/" + path)
        )
        return file_dir

    def GetPublicIP(self, retry=5):
        if retry == 0:
            return "127.0.0.1"

        try:
            response = requests.get("https://api.masterking32.com/ip.php?json=true")
            if response.status_code == 200:
                return response.json()["ipAddress"]
            else:
                return self.GetPublicIP(retry - 1)
        except Exception as e:
            # self.logger.error(f"{lc.r}Error: {e}{lc.rs}")
            return self.GetPublicIP(retry - 1)

    async def start(self):
        if os.name == "nt":
            self.SystemOS = "Windows"
        elif os.name == "posix":
            if os.uname().sysname == "Darwin":
                self.SystemOS = "Mac"
            else:
                self.SystemOS = "Linux"
        else:
            self.SystemOS = "Termux"

        self.logger.info(
            f"{lc.g}🖥️ You are running on {lc.rs + lc.y}{self.SystemOS}{lc.rs} {lc.g}OS{lc.rs}"
        )

        db = Database("database.db", self.logger)
        self.logger.info(f"{lc.g}🗺️ Getting public IP ...{lc.rs}")
        self.public_ip = self.GetPublicIP()
        self.logger.info(
            f"{lc.g}🗺️ Public IP: {lc.rs + lc.y}{utils.HideIP(self.public_ip)}{lc.rs}"
        )

        self.logger.info(f"{lc.g}🌐 Starting web server ...{lc.rs}")
        os.environ["FLASK_ENV"] = "production"
        flask.cli.show_server_banner = lambda *args: None

        self.app = Flask(__name__, template_folder=self.GetPublicHTMLPath(""))
        SecretKey = db.getSettings("flask_secret_key", None)
        if SecretKey is None:
            self.logger.info(f"{lc.y}🔐 Generating new secret key for flask ...{lc.rs}")
            SecretKey = "".join(
                random.choices(string.ascii_letters + string.digits, k=32)
            )
            db.queryScript(
                f"INSERT OR REPLACE INTO settings (name, value) VALUES ('flask_secret_key', '{SecretKey}');"
            )
            self.logger.info(f"{lc.g}🔐 Secret key generated successfully{lc.rs}")
        self.app.secret_key = SecretKey

        @self.app.route("/")
        def index():
            fileName = "index.html"
            template_path = self.GetPublicHTMLPath(fileName)
            db = Database("database.db", self.logger)
            theme = db.getSettings("theme", "dark")
            db.Close()
            if os.path.isfile(template_path):
                return render_template(
                    fileName, App_Version=vr.APP_VERSION, theme=theme
                )
            else:
                return "404 Not Found"

        @self.app.route("/<path:path>.py", methods=["GET", "POST"])
        def python_file(path):
            path = path.replace(".py", "")
            split_path = path.split("/")
            if len(split_path) != 2:
                return "404 Not Found"

            if (
                not split_path[0].isalnum()
                or not split_path[1].replace("_", "").isalnum()
            ):
                return "404 Not Found"

            file_path = self.GetControllersPath(f"{split_path[0]}.py")

            base_folder = self.GetControllersPath("")
            if base_folder not in file_path:
                return "403 Forbidden"

            if not os.path.isfile(file_path):
                return "404 Not Found"

            try:
                exec("import web.controllers." + split_path[0])
                Module = eval(
                    "web.controllers."
                    + split_path[0]
                    + "."
                    + split_path[0]
                    + "(self.logger)"
                )
                if hasattr(Module, split_path[1]):
                    return eval("Module" + "." + split_path[1] + "(request, self)")
                else:
                    return "404 Not Found"
            except Exception as e:
                self.logger.error(f"{lc.r}Error: {e}{lc.rs}")
                return "500 Internal Server Error"

        @self.app.route("/<path:path>")
        def static_file(path):
            base_folder = self.GetPublicHTMLPath("")

            file_dir = self.GetPublicHTMLPath(path)

            if base_folder not in file_dir or os.path.isdir(file_dir):
                return "403 Forbidden"

            if os.path.isfile(file_dir):
                if self.get_content_type(file_dir):
                    if self.get_content_type(file_dir) == "text/html":
                        # return render_template(path)
                        return "403 Forbidden"
                    try:
                        with open(file_dir, "rb") as f:
                            content = f.read()
                            f.close()
                        return (
                            content,
                            200,
                            {"Content-Type": self.get_content_type(file_dir)},
                        )
                    except FileNotFoundError:
                        return "404 Not Found"
                    except Exception as e:
                        self.logger.error(f"{lc.r}Error: {e}{lc.rs}")
                        return "500 Internal Server Error"
            return self.LoadFile(file_dir), 200

        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)
        self.logger.info(
            f"{lc.g}🌐 Web server started on 🔗 {lc.rs + lc.y}http://{self.host}:{self.port}{lc.rs} 🔗"
        )
        self.logger.info(
            f"{lc.g}🔐 Panel Password: {lc.rs + lc.r + db.getSettings('admin_password', 'admin') + lc.rs}"
        )

        db.Close()
        self.server = self.app.run(host=self.host, port=self.port, threaded=True)

    def get_content_type(self, path):
        extension = os.path.splitext(path)[1]
        content_types = {
            ".css": "text/css",
            ".js": "application/javascript",
            ".html": "text/html",
            ".png": "image/png",
            ".jpg": "image/jpg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
            ".ico": "image/x-icon",
            ".json": "application/json",
            ".woff": "font/woff",
            ".woff2": "font/woff2",
            ".ttf": "font/ttf",
            ".eot": "font/eot",
            ".otf": "font/otf",
        }

        return content_types.get(extension)

    def stop(self):
        self.logger.info(f"{lc.r}🌐 Stopping web server ...{lc.rs}")
        try:
            os.kill(os.getpid(), signal.SIGINT)
        except Exception as e:
            exit()
