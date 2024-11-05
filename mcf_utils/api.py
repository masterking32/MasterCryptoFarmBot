# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import requests
import json


class API:
    def __init__(self, logger):
        self.logger = logger

    def _post_request(self, url, data, retries=5):
        for _ in range(retries):
            try:
                response = requests.post(url, data=data)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 403:
                    return {"error": "License is not valid, please check your license"}
                elif "error" in response.text:
                    return response.json()
                else:
                    return {"error": "API Error: Please try again later"}
            except Exception as e:
                # self.logger.error(f"API Error: {e}")
                pass
        return None

    def __get_request(self, url, retries=5):
        for _ in range(retries):
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    return response.json()
            except Exception as e:
                # self.logger.error(f"API Error: {e}")
                pass
        return None

    def validate_license(self, license):
        data = {"license_key": license, "action": "get_license"}
        response = self._post_request(
            "https://api.masterking32.com/mcf_bot/api.php", data
        )
        if response and response.get("status") == "success":
            return response
        return None

    def get_modules(self, license):
        data = {"license_key": license, "action": "get_modules"}
        response = self._post_request(
            "https://api.masterking32.com/mcf_bot/api.php", data
        )
        if response:
            if response.get("status") == "success":
                return response
            return {
                "error": response.get(
                    "message", "Unable to get modules, please try again later"
                )
            }
        return {"error": "Unable to get modules, please try again later"}

    def install_module(self, license, module_id):
        data = {
            "license_key": license,
            "action": "install_module",
            "module_id": module_id,
        }
        response = self._post_request(
            "https://api.masterking32.com/mcf_bot/api.php", data
        )
        if response:
            if response.get("status") == "success":
                return response
            return {
                "error": response.get(
                    "message", "Unable to install module, please try again later"
                )
            }
        return {"error": "Unable to install module, please try again later"}

    def get_mcf_version(self):
        response = self._post_request(
            "https://api.masterking32.com/mcf_bot/mcf_version.php",
            data={"action": "get_mcf_version"},
        )
        if response and "commit_hash" in response and "commit_date" in response:
            return response
        return None

    def get_user_modules(self, license):
        if license == "Free License":
            return None

        data = {"license_key": license, "action": "get_user_modules"}
        response = self._post_request(
            "https://api.masterking32.com/mcf_bot/api.php", data
        )
        if response and response.get("status") == "success" and "modules" in response:
            return response["modules"]
        return None

    def get_public_ip(self, retry=5):
        if retry == 0:
            return "127.0.0.1"

        try:
            response = requests.get("https://api.masterking32.com/ip.php?json=true")
            if response.status_code == 200:
                return response.json()["ipAddress"]
            else:
                return self.get_public_ip(retry - 1)
        except Exception:
            return self.get_public_ip(retry - 1)

    def check_telegram_access(self, retries=3):
        telegram_api_url = "https://api.telegram.org/connection-test"

        try:
            response = requests.get(telegram_api_url, timeout=5)
            # This request should return 404
            # cause it's not a valid endpoint
            # but it's used to check if the bot has access to the telegram API
            if response.status_code == 404:
                json_response = response.json()
                if "ok" in json_response:
                    return True

            return False
        except Exception:
            pass

        if retries > 0:
            return self.check_telegram_access(retries - 1)

        return False

    def get_task_answer(self, license_key, data):
        if license_key is None:
            return None

        try:
            data["license_key"] = license_key
            response = self._post_request(
                "https://api.masterking32.com/mcf_bot/api.php", data
            )

            if response is None:
                return None

            return response
        except Exception as e:
            self.log.error(f"<r>⭕ {e} failed to get data!</r>")
            return None

    def get_tv(self, license_key, tool_name):
        if license_key is None:
            return None

        data = {
            "license_key": license_key,
            "tool_name": tool_name,
            "action": "tools_version",
        }

        try:
            response = self._post_request(
                "https://api.masterking32.com/mcf_bot/api.php", data
            )

            if response is None:
                return None

            return response

        except Exception as e:
            self.log.error(f"<r>⭕ {e} failed to get data!</r>")
            return None
