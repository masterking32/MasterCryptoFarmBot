# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import signal
import time
import requests

import utils.logColors as lc
import utils.utils as utils
import os


class Git:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config

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
        self.logger.error(
            f"{lc.r} ❌ You need install project as git repository{lc.rs}"
        )
        self.logger.error(
            f"{lc.r} ❌ Please remove the project and clone it again{lc.rs}"
        )
        self.logger.error(
            f"{lc.r} ❌ If you have any changes, Please backup it before removing{lc.rs}"
        )
        self.logger.error(
            f"{lc.r} ❌ To clone the project, Please run the following command:{lc.rs}"
        )

        self.logger.error(
            f"{lc.g} ❯ git clone https://github.com/masterking32/MasterCryptoFarmBot{lc.rs}"
        )
        os.kill(os.getpid(), signal.SIGINT)
        return None

    def GitHasCommit(self, commit_hash):
        try:
            response = (
                os.popen(
                    f"git cat-file -t {commit_hash} 2>/dev/null"
                    if os.name != "nt"
                    else f"git cat-file -t {commit_hash} 2>nul"
                )
                .read()
                .strip()
            )
            if response == "commit":
                return True
        except Exception as e:
            pass

        return False

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

    def UpdateProject(self):
        self.logger.info(f"{lc.g}🔄 Updating project ...{lc.rs}")

        try:
            (
                os.popen(
                    "git pull 2>/dev/null" if os.name != "nt" else "git pull 2>nul"
                )
                .read()
                .strip()
            )
            self.logger.info(f"{lc.g}🔄 Project updated successfully{lc.rs}")
            self.logger.info(f"{lc.g}🔄 Stopping project ...{lc.rs}")
            os.kill(os.getpid(), signal.SIGINT)
            return True
        except Exception as e:
            self.logger.error(
                f"{lc.r} ❌ Error while updating project, Please update manually{lc.rs}"
            )

        return False

    def gitClone(self, url, directory):
        self.logger.info(f"{lc.g}🔄 Cloning project ...{lc.rs}")

        try:
            (
                os.popen(
                    f"git clone {url} {directory} 2>/dev/null"
                    if os.name != "nt"
                    else f"git clone {url} {directory} 2>nul"
                )
                .read()
                .strip()
            )
            self.logger.info(f"{lc.g}🔄 Project cloned successfully{lc.rs}")
            return True
        except Exception as e:
            self.logger.error(
                f"{lc.r} ❌ Error while cloning project, Please clone manually{lc.rs}"
            )

        return False
