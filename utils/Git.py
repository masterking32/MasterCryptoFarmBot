# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import signal

import utils.logColors as lc
import os


class Git:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config

    def GetRecentLocalCommit(self, directory=None):
        try:
            if not directory:
                directory = os.getcwd()

            response = (
                os.popen(
                    f'cd "{directory}" && git log -1 --pretty=format:%H 2>/dev/null'
                    if os.name != "nt"
                    else f'cd "{directory}" && git log -1 --pretty=format:%H 2>nul'
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

    def GitHasCommit(self, commit_hash, directory=None):
        try:
            if not directory:
                directory = os.getcwd()
            response = (
                os.popen(
                    f'cd "{directory}" && git cat-file -t {commit_hash} 2>/dev/null'
                    if os.name != "nt"
                    else f'cd "{directory}" && git cat-file -t {commit_hash} 2>nul'
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

    def UpdateProject(self, directory=None, RestartAfterUpdate=True):
        ProjecTName = "Project"
        if directory is not None:
            ProjecTName = directory.split("/")[-1]

        self.logger.info(f"{lc.g}🔄 Updating {ProjecTName} ...{lc.rs}")

        try:
            if not directory:
                directory = os.getcwd()

            (
                os.popen(
                    f'cd "{directory}" && git pull 2>/dev/null'
                    if os.name != "nt"
                    else f'cd "{directory}" && git pull 2>nul'
                )
                .read()
                .strip()
            )
            if ProjecTName == "Project":
                self.logger.info(
                    f"{lc.g}└─ ✅ {ProjecTName} updated successfully{lc.rs}"
                )

            if RestartAfterUpdate:
                self.logger.info(f"{lc.g}└─ 🛑 Stopping project ...{lc.rs}")
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
