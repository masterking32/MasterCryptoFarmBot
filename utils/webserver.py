# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import os
from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler

import utils.logColors as lc


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
            f"{lc.g}🌐 Web server started on http://{self.host}:{self.port} ...{lc.rs}"
        )

        self.logger.info(
            f"{lc.g}🔐 Panel Password: {lc.rs + lc.r + self.admin_password + lc.rs}"
        )
        self.server.serve_forever()

    def stop(self):
        self.logger.info(f"{lc.r}🌐 Stopping web server ...{lc.rs}")
        self.server.shutdown()
        self.server.server_close()

    def WebServerHandler(self, request, client_address, server):
        class WebServerHandler(SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/":
                    self.path = "/index.html"

                content_type = self.get_content_type(self.path)
                if content_type is None:
                    self.send_response(404)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"404 Not Found")
                    return

                self.send_response(200)
                self.send_header("Content-type", content_type)
                self.end_headers()
                with open(f"web/public_html{self.path}", "rb") as file:
                    self.wfile.write(file.read())

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
