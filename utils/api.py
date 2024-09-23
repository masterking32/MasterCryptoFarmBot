import requests
import json


class API:
    def __init__(self, logger):
        self.logger = logger

    def ValidateLicense(self, license, retries=5):
        if retries == 0:
            return None

        try:
            retries -= 1
            response = requests.post(
                "https://api.masterking32.com/mcf_bot/api.php",
                data={"license_key": license, "action": "get_license"},
            )
            if response.status_code == 200:
                response = json.loads(response.text)
                if response["status"] == "success":
                    return response
                else:
                    return None
            else:
                return None
        except Exception as e:
            # self.logger.error(f"API Error: {e}")
            return self.ValidateLicense(license, retries)

    def GetModules(self, license, retires=5):
        if retires == 0:
            return {"error": "Unable to get modules, please try again later!"}

        try:
            retires -= 1
            response = requests.post(
                "https://api.masterking32.com/mcf_bot/api.php",
                data={"license_key": license, "action": "get_modules"},
            )
            if response.status_code == 200:
                response = json.loads(response.text)
                if response["status"] == "success":
                    return response
                else:
                    return {"error": response["message"]}
            elif response.status_code == 403:
                return {"error": "License is not valid, please check your license"}
            else:
                return {"error": "Unable to get modules, please try again later"}
        except Exception as e:
            # self.logger.error(f"API Error: {e}")
            return self.GetModules(license, retires)

    def InstallModule(self, license, moduleID, retries=5):
        if retries == 0:
            return {"error": "Unable to install module, please try again later!"}

        try:
            retries -= 1
            response = requests.post(
                "https://api.masterking32.com/mcf_bot/api.php",
                data={
                    "license_key": license,
                    "action": "install_module",
                    "module_id": moduleID,
                },
            )
            if response.status_code == 200:
                response = json.loads(response.text)
                if response["status"] == "success":
                    return response
                else:
                    return {"error": response["message"]}
            elif response.status_code == 403:
                return {"error": "License is not valid, please check your license"}
            elif response.status_code == 400 and "error" in response:
                return {"error": response["error"]}
            else:
                return {"error": "Unable to install module, please try again later"}
        except Exception as e:
            # self.logger.error(f"API Error: {e}")
            return self.InstallModule(license, moduleID, retries)

    def GetMCFVersion(self, retries=5):
        if retries == 0:
            return None

        retries -= 1
        try:
            response = requests.get(
                "https://api.masterking32.com/mcf_bot/mcf_version.php"
            )
            if response.status_code == 200:
                return json.loads(response.text)
            else:
                return self.GetMCFVersion(retries)
        except Exception as e:
            # self.logger.error(f"API Error: {e}")
            return self.GetMCFVersion(retries)
