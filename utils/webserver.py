# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import os
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler

import utils.logColors as lc
import utils.variables as var
import importlib


class WebServer:
    def __init__(self, logger, db, config):
        self.logger = logger
        self.db = db
        self.config = config
        self.admin_password = db.getSettings("admin_password", "admin")
        self.host = self.config["web_server"]["host"]
        self.port = self.config["web_server"]["port"]
        self.server = None

    async def start(self):
        self.logger.info(f"{lc.g}🌐 Starting web server ...{lc.rs}")
        self.server = HTTPServer((self.host, self.port), self.WebServerHandler)
        self.logger.info(
            f"{lc.g}🌐 Web server started on 🔗 {lc.rs + lc.y}http://{self.host}:{self.port}{lc.rs} 🔗"
        )

        self.logger.info(
            f"{lc.g}🔐 Panel Password: {lc.rs + lc.r + self.admin_password + lc.rs}"
        )
        self.server.serve_forever()

    def stop(self):
        self.logger.info(f"{lc.r}🌐 Stopping web server ...{lc.rs}")
        self.server.shutdown()
        self.server.server_close()

    def TemplateEngine(self, template, data):
        default_data = {
            "APP_VERSION": var.APP_VERSION,
            "ERROR_MESSAGE": "",
            "HAS_ERROR": "hidden",
        }

        data_new = {**default_data, **data}
        for key, value in default_data.items():
            if key in data:
                data_new[key] = data[key]

        for key, value in data_new.items():
            template = template.replace(f"{{{{{key}}}}}", value)

        return template

    def deleteOldSessions(self):
        try:
            session_dir = "temp"
            files = [
                file for file in os.listdir(session_dir) if file.startswith("sessions_")
            ]
            for file in files:
                file_path = os.path.join(session_dir, file)
                file_create_time = os.path.getctime(file_path)
                if (time.time() - file_create_time) / 3600 > 6:
                    os.remove(file_path)
                    self.logger.info(f"{lc.y}🗑️ Deleted old session file: {file}{lc.rs}")
        except Exception as e:
            self.logger.error(f"deleteOldSessions: {e}")

    def CheckAuth(self, request):
        self.deleteOldSessions()
        if "Cookie" not in request.headers:
            return False

        cookie = request.headers.get("Cookie")
        if not cookie or "auth" not in cookie:
            return False

        auth_token = cookie.split("=")[1]
        if len(auth_token) != 64 or not auth_token.isalnum():
            return False

        session_file = f"temp/sessions_{auth_token}.json"
        if not os.path.exists(session_file):
            return False

        return True

    def SendHTML(self, request, content):
        try:
            request.send_response(200)
            request.send_header("Content-type", "text/html")
            request.end_headers()
            request.wfile.write(content)
        except Exception as e:
            self.logger.error(f"SendHTML: {e}")

    def SendError(self, request, code):
        try:
            request.send_response(code)
            request.send_header("Content-type", "text/html")
            request.end_headers()
            request.wfile.write(f"{code} Error".encode("utf-8"))
        except Exception as e:
            self.logger.error(f"SendError: {e}")

    def SendRedirect(self, request, location):
        try:
            request.send_response(302)
            request.send_header("Location", location)
            request.end_headers()
        except Exception as e:
            self.logger.error(f"SendRedirect: {e}")

    def WebServerHandler(self, request, client_address, server):
        WebServerGlobal = self

        Routing = {
            "/auth/login.html": "web/controllers/LoginController.py",
        }

        class WebServerHandler(SimpleHTTPRequestHandler):
            def do_POST(self):
                try:
                    if self.path in Routing:
                        if not os.path.exists(Routing[self.path]):
                            WebServerGlobal.SendError(self, 404)
                            return

                        fileName = os.path.basename(Routing[self.path])
                        ClassName = fileName.split(".")[0]
                        if ClassName not in globals():
                            module = importlib.import_module(
                                Routing[self.path].replace("/", ".")[:-3]
                            )
                            globals()[ClassName] = getattr(module, ClassName)

                        controller = globals()[ClassName](WebServerGlobal)
                        controller.post(self)

                    else:
                        WebServerGlobal.SendError(self, 404)
                        return
                except Exception as e:
                    WebServerGlobal.SendError(self, 500)
                    WebServerGlobal.logger.error(f"WebServerHandler POST: {e}")

            def do_GET(self):
                try:
                    if self.path == "/":
                        self.path = "/index.html"

                    if "/auth/" in self.path:
                        if WebServerGlobal.CheckAuth(self):
                            WebServerGlobal.SendRedirect(self, "/admin/dashboard.html")
                            return

                    if "/admin/" in self.path:
                        if not WebServerGlobal.CheckAuth(self):
                            WebServerGlobal.SendRedirect(self, "/auth/login.html")
                            return

                    file_path = f"web/public_html{self.path}"
                    if not os.path.exists(file_path):
                        WebServerGlobal.SendError(self, 404)
                        return

                    content_type = self.get_content_type(self.path)
                    if content_type is None:
                        WebServerGlobal.SendError(self, 404)
                        return

                    with open(file_path, "r") as file:
                        content = file.read()
                        if content_type == "text/html":
                            content = WebServerGlobal.TemplateEngine(content, {})

                        content = content.encode("utf-8")
                        self.send_response(200)
                        self.send_header("Content-type", content_type)
                        self.end_headers()
                        self.wfile.write(content)
                        return

                except ConnectionAbortedError:
                    return
                except Exception as e:
                    WebServerGlobal.SendError(self, 500)
                    WebServerGlobal.logger.error(f"WebServerHandler: {e}")

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

            def log_message(self, format, *args):
                pass

        return WebServerHandler(request, client_address, server)
