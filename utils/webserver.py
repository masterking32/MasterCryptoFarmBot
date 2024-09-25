# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import os
import platform
import random
import string
import logging
from flask import Flask, render_template, request, send_from_directory
import flask.cli
from utils.database import Database
import utils.variables as vr
import utils.utils as utils
import utils.api as api


class WebServer:
    def __init__(self, logger, config, module_threads):
        self.logger = logger
        self.config = config
        self.host = self.config["web_server"]["host"]
        self.port = self.config["web_server"]["port"]
        self.server = None
        self.public_ip = "127.0.0.1"
        self.system_os = None
        self.module_threads = module_threads

    def load_file(self, file):
        try:
            with open(file, "r") as f:
                return f.read()
        except FileNotFoundError:
            return "404 Not Found"
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return "500 Internal Server Error"

    def get_public_html_path(self, path):
        current_dir = os.path.dirname(__file__)
        return os.path.abspath(os.path.join(current_dir, "../web/public_html/", path))

    def get_controllers_path(self, path):
        current_dir = os.path.dirname(__file__)
        return os.path.abspath(os.path.join(current_dir, "../web/controllers/", path))

    async def start(self):
        self.system_os = platform.system()
        self.logger.info(
            f"<green>🖥️ System OS: </green><yellow>{self.system_os}</yellow>"
        )

        db = Database("database.db", self.logger)
        self.logger.info("<green>🗺️ Getting public IP ...</green>")
        apiObj = api.API(self.logger)
        self.public_ip = apiObj.get_public_ip()
        self.logger.info(
            f"<green>🗺️ Public IP: </green><yellow>{utils.HideIP(self.public_ip)}</yellow>"
        )

        self.logger.info("<green>🌐 Starting Web Server ...</green>")
        os.environ["FLASK_ENV"] = "production"
        flask.cli.show_server_banner = lambda *args: None

        self.app = Flask(__name__, template_folder=self.get_public_html_path(""))

        secret_key = db.getSettings("flask_secret_key", None)
        if secret_key is None:
            self.logger.info("<green>🔐 [Flask] Generating secret key ...</green>")
            secret_key = "".join(
                random.choices(string.ascii_letters + string.digits, k=32)
            )
            db.queryScript(
                f"INSERT OR REPLACE INTO settings (name, value) VALUES ('flask_secret_key', '{secret_key}');"
            )
            self.logger.info("<green>└─ ✅ Secret key generated successfully</green>")
        self.app.secret_key = secret_key

        @self.app.route("/")
        def index():
            file_name = "index.html"
            template_path = self.get_public_html_path(file_name)
            theme = db.getSettings("theme", "dark")
            if os.path.isfile(template_path):
                return render_template(
                    file_name, App_Version=vr.APP_VERSION, theme=theme
                )
            else:
                return "404 Not Found"

        @self.app.route("/<path:path>.py", methods=["GET", "POST"])
        def python_file(path):
            path = path.replace(".py", "")
            split_path = path.split("/")
            if len(split_path) != 2 or not all(
                part.isalnum() or part.replace("_", "").isalnum() for part in split_path
            ):
                return "404 Not Found"

            if split_path[1].startswith("_"):
                return "404 Not Found"

            file_path = self.get_controllers_path(f"{split_path[0]}.py")
            base_folder = self.get_controllers_path("")
            if not file_path.startswith(base_folder) or not os.path.isfile(file_path):
                return "404 Not Found"

            try:
                exec(f"import web.controllers.{split_path[0]}")
                module = eval(
                    f"web.controllers.{split_path[0]}.{split_path[0]}(self.logger)"
                )
                if hasattr(module, split_path[1]):
                    return eval(f"module.{split_path[1]}(request, self)")
                else:
                    return "404 Not Found"
            except Exception as e:
                self.logger.error(f"Error: {e}")
                return "500 Internal Server Error"

        @self.app.route("/<path:path>")
        def static_file(path):
            base_folder = self.get_public_html_path("")
            file_dir = self.get_public_html_path(path)

            if not file_dir.startswith(base_folder):
                return "404 Not Found"
            if os.path.isdir(file_dir):
                return "403 Forbidden"
            if os.path.exists(file_dir) and os.path.isfile(file_dir):
                content_type = self.get_content_type(file_dir)
                if content_type == "text/html":
                    return "403 Forbidden"
                try:
                    return send_from_directory(base_folder, path)
                except FileNotFoundError:
                    return "404 Not Found"
                except Exception as e:
                    self.logger.error(f"<red>Error: {e}</red>")
                    return "500 Internal Server Error"
            else:
                return "404 Not Found"

        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)
        self.logger.info(
            f"<green>⚙️ To access the panel, visit: </green>🌐<b><yellow> http://{self.host}:{self.port} </yellow></b>🌐"
        )
        self.logger.info(
            f"<green>🔐 Panel Password: </green><red>{db.getSettings('admin_password', 'admin')}</red>"
        )

        self.server = self.app.run(host=self.host, port=self.port, threaded=True)

    def get_content_type(self, path):
        extension = os.path.splitext(path)[1].lower()
        content_types = {
            ".css": "text/css",
            ".js": "application/javascript",
            ".html": "text/html",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
            ".ico": "image/x-icon",
            ".json": "application/json",
            ".woff": "font/woff",
            ".woff2": "font/woff2",
            ".ttf": "font/ttf",
            ".eot": "application/vnd.ms-fontobject",
            ".otf": "font/otf",
        }
        return content_types.get(extension, "application/octet-stream")
