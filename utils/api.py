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
                    return json.loads(response.text)
                elif response.status_code == 403:
                    return {"error": "License is not valid, please check your license"}
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
                    return json.loads(response.text)
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
        response = self.__get_request(
            "https://api.masterking32.com/mcf_bot/mcf_version.php"
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
