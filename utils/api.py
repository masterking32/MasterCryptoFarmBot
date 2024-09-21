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
