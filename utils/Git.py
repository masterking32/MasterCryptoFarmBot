# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import requests

import utils.logColors as lc
import os


class Git:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config

    def GetGitHubRecentCommit(self, repository):
        try:
            response = requests.get(
                f"https://api.github.com/repos/{repository}/commits"
            )
            if response.status_code == 200:
                return response.json()[0]
        except Exception as e:
            self.logger.error(f"{lc.r}Error: {e}{lc.rs}")

        return None

    def GetRecentLocalCommit(self):
        try:
            response = (
                os.popen(
                    "git log -1 --pretty=format:%H 2>/dev/null"
                    if os.name != "nt"
                    else "git log -1 --pretty=format:%H 2>nul"
                )
                .read()
                .strip()
            )
            if response and len(response) == 40:
                return response
            else:
                self.logger.error(
                    f"{lc.r} ❌ Project is not a git repository, Please initialize git{lc.rs}"
                )
        except Exception as e:
            self.logger.error(
                f"{lc.r} ❌ Project is not a git repository, Please initialize git{lc.rs}"
            )

        return None

    def CheckGitInstalled(self):
        try:
            response = (
                os.popen(
                    "git --version 2>/dev/null"
                    if os.name != "nt"
                    else "git --version 2>nul"
                )
                .read()
                .strip()
            )
            if response:
                return True
            else:
                self.logger.error(
                    f"{lc.r} ❌ Git is not installed, Please install git{lc.rs}"
                )
        except Exception as e:
            self.logger.error(
                f"{lc.r} ❌ Git is not installed, Please install git{lc.rs}"
            )

        return False
