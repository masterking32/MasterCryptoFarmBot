# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import os

import utils.logColors as lc
import utils.Git as Git
import utils.utils as utils
import utils.api as api
import utils.database as database
import config


class Module:
    def __init__(self, logger):
        self.logger = logger
        self.module_list = []

    def get_ModuleName(self):
        return os.path.basename(os.getcwd())

    def is_module_disabled(self, db, module_name):
        return db.getSettings(f"{module_name}_disabled", "0") == "1"

    def load_modules(self, noLog=False):
        if not noLog:
            self.logger.info(f"{lc.g}🔍 Loading modules ...{lc.rs}")

        if not os.path.exists("modules"):
            if not noLog:
                self.logger.info(f"{lc.y}📁 Creating modules directory ...{lc.rs}")
            os.makedirs("modules")

        modules = os.listdir("modules")
        apiObj = api.API(self.logger)

        db = database.Database("database.db", self.logger)
        license = db.getSettings("license", "Free License")
        db.Close()

        license_modules = apiObj.GetUserModules(license)
        if not license_modules:
            license_modules = []

        for module in modules:
            if os.path.isdir(f"modules/{module}"):
                if not os.listdir(f"modules/{module}"):
                    continue

                if not os.path.exists(f"modules/{module}/bot.py"):
                    if not noLog:
                        self.logger.warning(
                            f"{lc.y}└─ ⚠️ {module} bot.py not found!{lc.rs}"
                        )
                    continue

                commit_hash = None
                module_found = False
                for l_module in license_modules:
                    if l_module["name"] == module:
                        if not l_module["enabled"]:
                            if not noLog:
                                self.logger.warning(
                                    f"{lc.y}└─ ⚠️ {module} is disabled in license!{lc.rs}"
                                )
                            continue
                        commit_hash = l_module["commit_hash"]
                        module_found = True

                if (
                    utils.getConfig(config.config, "auto_update_modules", True)
                    and commit_hash is not None
                ):
                    if self.UpdateRequired(module, commit_hash):
                        git = Git.Git(self.logger, None)
                        directory = os.path.join(os.getcwd(), f"modules/{module}")
                        git.UpdateProject(directory, False)
                    else:
                        if not noLog:
                            self.logger.info(
                                f"{lc.g}└─ ✅ {lc.rs + lc.c}{module}{lc.rs + lc.g} is up to date!{lc.rs}"
                            )
                if not module_found and not noLog:
                    self.logger.warning(
                        f"{lc.y}└─ ⚠️ {lc.rs + lc.c}{module}{lc.rs + lc.y} is unverified!{lc.rs}"
                    )

                self.module_list.append(module)
                if not noLog:
                    self.logger.info(
                        f"{lc.g}└─ ✅ {lc.rs + lc.c}{module}{lc.rs + lc.g} loaded!{lc.rs}"
                    )

        if not noLog:
            self.logger.info(
                f"✅ {lc.c}{len(self.module_list)}{lc.rs + lc.g} modules loaded!{lc.rs}"
            )

    def UpdateRequired(self, module, new_commit_hash):
        if not os.path.exists(f"modules/{module}/.git"):
            return False

        if not new_commit_hash:
            return False

        try:
            git = Git.Git(self.logger, None)
            current_commit_hash = git.GetRecentLocalCommit(f"modules/{module}")
            return current_commit_hash != new_commit_hash
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return False
