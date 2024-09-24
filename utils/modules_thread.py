# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import os
import time

import utils.logColors as lc
import utils.Git as Git
import utils.utils as utils
import utils.api as api
import utils.database as database
from utils.modules import Module
import config


class Module_Thread:
    def __init__(self, logger):
        self.logger = logger
        self.api = api.API(self.logger)

    def getModules(self, Update=False):
        if not os.path.exists("modules"):
            return []

        modules = os.listdir("modules")

        db = database.Database("database.db", self.logger)
        license = db.getSettings("license", "Free License")

        license_modules = None
        if license != "Free License" and Update:
            license_modules = self.api.GetUserModules(license)

        if license_modules is None:
            license_modules = []

        modules_output = []
        for module in modules:
            if not os.path.isdir(f"modules/{module}") or not os.path.exists(
                f"modules/{module}/bot.py"
            ):
                continue

            new_module = {
                "name": module,
                "commit_hash": None,
                "restart_required": False,
                "disabled": db.getSettings(f"{module}_disabled", "0") == "1",
            }

            if new_module["disabled"]:
                modules_output.append(new_module)
                continue

            try:
                git = Git.Git(self.logger, config.config)
                modules_class = Module(self.logger)
                for l_module in license_modules:
                    if l_module["name"] == module:
                        if not l_module["enabled"]:
                            new_module["disabled"] = True
                        new_module["commit_hash"] = l_module["commit_hash"]
                        break

                if not Update:
                    modules_output.append(new_module)
                    continue

                if (
                    utils.getConfig(config.config, "auto_update_modules", True)
                    and new_module["commit_hash"] is not None
                    and modules_class.UpdateRequired(module, new_module["commit_hash"])
                ):
                    new_module["restart_required"] = True
                    directory = os.path.join(os.getcwd(), f"modules/{module}")
                    git.UpdateProject(directory, False)
                    db.migration_modules([module])
            except Exception as e:
                self.logger.error(f"Modules Thread: {e}")

            modules_output.append(new_module)

        db.Close()
        return modules_output

    def CheckMainProjectUpdate(self):
        try:
            if not utils.getConfig(config.config, "auto_update", True):
                return

            git = Git.Git(self.logger, config.config)
            localGitCommit = git.GetRecentLocalCommit()
            if localGitCommit is None:
                return

            mcf_version = self.api.GetMCFVersion()
            if mcf_version is None:
                return

            commit_hash = mcf_version["commit_hash"]

            if not git.GitHasCommit(commit_hash):
                self.logger.error(f"{lc.r}🔄 Main Project is not updated ... {lc.rs}")
                git.UpdateProject()
                self.logger.error(f"{lc.r}🔄 Please restart the bot ... {lc.rs}")
        except Exception as e:
            self.logger.error(f"CheckMainProjectUpdate: {e}")

    def UpdateCheckThread(self):
        if not utils.getConfig(config.config, "auto_update_modules", True):
            return
        update_check_interval = utils.getConfig(
            config.config, "update_check_interval", 1200
        )

        if update_check_interval < 600:
            update_check_interval = 600

        while True:
            self.logger.info(f"{lc.g}🔄 Checking for updates ...{lc.rs}")
            self.CheckMainProjectUpdate()
            try:
                modules = self.getModules(Update=True)
                for module in modules:
                    if module["restart_required"]:
                        self.logger.warning(
                            f"{lc.y}└─ 🔄 Module Restart required for {lc.c}{module['name']}{lc.y} module ...{lc.rs}"
                        )
                        # restart module.

                self.logger.info(f"{lc.g}└─ ✅ Update check completed!{lc.rs}")
                time.sleep(update_check_interval)
            except Exception as e:
                self.logger.error(f"UpdateCheckThread: {e}")
                time.sleep(update_check_interval)
