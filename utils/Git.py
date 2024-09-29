# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import subprocess
import signal
import os
import utils.logColors as lc


class Git:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config

    def _run_git_command(self, command, directory):
        try:
            result = subprocess.run(
                command,
                cwd=directory,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return result.stdout.strip()
        except Exception as e:
            self.logger.error(f"<red> ❌ Error running git command: {e}</red>")
            return None

    def GetRecentLocalCommit(self, directory=None):
        directory = directory or os.getcwd()
        response = self._run_git_command("git log -1 --pretty=format:%H", directory)
        if response and len(response) == 40:
            return response
        self._log_git_error()
        return None

    def GitHasCommit(self, commit_hash, directory=None):
        directory = directory or os.getcwd()
        response = self._run_git_command(f"git cat-file -t {commit_hash}", directory)
        return response == "commit"

    def CheckGitInstalled(self):
        response = self._run_git_command("git --version", None)
        if response:
            return True
        self.logger.error(f"<red> ❌ Git is not installed, Please install git</red>")
        return False

    def UpdateProject(self, directory=None, RestartAfterUpdate=True):
        directory_path = directory or os.getcwd()
        project_name = "Project" if directory is None else directory.split("/")[-1]
        self.logger.info(f"<green>🔄 Updating <cyan>{project_name}</cyan> ...</green>")

        response = self._run_git_command("git pull", directory_path)

        if response is None:
            self.logger.error(
                f"<red> ❌ Error while updating project, Please update manually</red>"
            )

        if "Already up to date." in response:
            self.logger.info(
                f"<green>└─ ✅ <cyan>{project_name}</cyan> updated successfully</green>"
            )
            if RestartAfterUpdate:
                self.logger.info(f"<green>└─ 🛑 Stopping project ...</green>")
                os.kill(os.getpid(), signal.SIGINT)
            return True

        if (
            "stash" in response
            or "deletions" in response
            or "insertions" in response
            or "file changed" in response
        ):
            self.logger.info(
                f"<green>└─ ✅ <cyan>{project_name}</cyan> updated successfully</green>"
            )
            if RestartAfterUpdate:
                self.logger.info(f"<green>└─ 🛑 Stopping project ...</green>")
                os.kill(os.getpid(), signal.SIGINT)
            return True

        self.logger.error(
            f"<red> ❌ Error while updating project, Please update manually</red>"
        )

        if RestartAfterUpdate:
            self.logger.info(f"<green>└─ 🛑 Stopping project ...</green>")
            os.kill(os.getpid(), signal.SIGINT)
        return False

    def gitClone(self, url, directory):
        self.logger.info(f"<green>🔄 Cloning project ...</green>")
        response = self._run_git_command(f"git clone {url} {directory}", None)
        if response is not None:
            self.logger.info(f"<green>🔄 Project cloned successfully</green>")
            return True
        self.logger.error(
            f"<red> ❌ Error while cloning project, Please clone manually</red>"
        )
        return False

    def _log_git_error(self):
        self.logger.error(
            f"<red> ❌ Project is not a git repository, Please initialize git</red>"
        )
        self.logger.error(
            f"<red> ❌ You need to install the project as a git repository</red>"
        )
        self.logger.error(
            f"<red> ❌ Please remove the project and clone it again</red>"
        )
        self.logger.error(
            f"<red> ❌ If you have any changes, Please backup them before removing</red>"
        )
        self.logger.error(
            f"<red> ❌ To clone the project, Please run the following command:</red>"
        )
        self.logger.error(
            f"<green> ❯ git clone https://github.com/masterking32/MasterCryptoFarmBot</green>"
        )
        os.kill(os.getpid(), signal.SIGINT)
