# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import random
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs

import utils.logColors as lc


class LoginController:
    def __init__(self, webserver):
        self.webserver = webserver

    def post(self, request):
        try:
            content_length = int(request.headers["Content-Length"])
            post_data = request.rfile.read(content_length).decode("utf-8")
            post_data = parse_qs(post_data)

            if "password" not in post_data:
                request.send_response(302)
                request.send_header("Location", "/auth/login.html")
                request.end_headers()
                request.wfile.write(b"302 Redirect")
                return
            password = post_data["password"][0]

            if password == self.webserver.admin_password:
                self.webserver.logger.info(
                    f"🔓 {lc.g}Successful login from {lc.rs + lc.r + request.client_address[0] + lc.rs}"
                )
                sessionID = "".join(
                    random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=64)
                )

                # create session file
                with open("temp/sessions_" + sessionID + ".json", "w") as file:
                    file.close()
                request.send_response(302)
                request.send_header("Set-Cookie", f"auth={sessionID}; Path=/")
                request.send_header("Location", "/admin/dashboard.html")
                request.end_headers()
                request.wfile.write(b"302 Redirect")
            else:
                self.webserver.logger.warning(
                    f"🔒 {lc.y}Invalid password: { lc.rs + lc.c + password + lc.rs + lc.y} from {lc.rs + lc.r + request.client_address[0] + lc.rs}"
                )
                with open("web/public_html/auth/login.html", "r") as file:
                    content = file.read()
                    content = self.webserver.TemplateEngine(
                        content,
                        {"ERROR_MESSAGE": "Invalid password", "HAS_ERROR": "has-error"},
                    )

                    content = content.encode("utf-8")
                    request.send_response(200)
                    request.send_header("Content-type", "text/html")
                    request.end_headers()
                    request.wfile.write(content)

        except Exception as e:
            request.send_response(500)
            request.send_header("Content-type", "text/html")
            request.end_headers()
            request.wfile.write(b"500 Internal Server Error")
            self.webserver.logger.error(f"LoginController: {e}")
