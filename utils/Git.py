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
            self.logger.error(f"{lc.r} ❌ Error running git command: {e}{lc.rs}")
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
        self.logger.error(f"{lc.r} ❌ Git is not installed, Please install git{lc.rs}")
        return False

    def UpdateProject(self, directory=None, RestartAfterUpdate=True):
        directory = directory or os.getcwd()
        project_name = directory.split("/")[-1] if directory else "Project"
        self.logger.info(
            f"{lc.g}🔄 Updating {lc.rs + lc.c}{project_name}{lc.rs + lc.g} ...{lc.rs}"
        )

        response = self._run_git_command("git pull", directory)
        if response is not None:
            self.logger.info(
                f"{lc.g}└─ ✅ {lc.rs + lc.c}{project_name}{lc.rs + lc.g} updated successfully{lc.rs}"
            )
            if RestartAfterUpdate:
                self.logger.info(f"{lc.g}└─ 🛑 Stopping project ...{lc.rs}")
                os.kill(os.getpid(), signal.SIGINT)
            return True
        self.logger.error(
            f"{lc.r} ❌ Error while updating project, Please update manually{lc.rs}"
        )
        return False

    def gitClone(self, url, directory):
        self.logger.info(f"{lc.g}🔄 Cloning project ...{lc.rs}")
        response = self._run_git_command(f"git clone {url} {directory}", None)
        if response is not None:
            self.logger.info(f"{lc.g}🔄 Project cloned successfully{lc.rs}")
            return True
        self.logger.error(
            f"{lc.r} ❌ Error while cloning project, Please clone manually{lc.rs}"
        )
        return False

    def _log_git_error(self):
        self.logger.error(
            f"{lc.r} ❌ Project is not a git repository, Please initialize git{lc.rs}"
        )
        self.logger.error(
            f"{lc.r} ❌ You need to install the project as a git repository{lc.rs}"
        )
        self.logger.error(
            f"{lc.r} ❌ Please remove the project and clone it again{lc.rs}"
        )
        self.logger.error(
            f"{lc.r} ❌ If you have any changes, Please backup them before removing{lc.rs}"
        )
        self.logger.error(
            f"{lc.r} ❌ To clone the project, Please run the following command:{lc.rs}"
        )
        self.logger.error(
            f"{lc.g} ❯ git clone https://github.com/masterking32/MasterCryptoFarmBot{lc.rs}"
        )
        os.kill(os.getpid(), signal.SIGINT)
