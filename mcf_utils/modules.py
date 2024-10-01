# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import os

import mcf_utils.Git as Git
import mcf_utils.utils as utils
import mcf_utils.api as api
import mcf_utils.database as database
import config


class Module:
    def __init__(self, logger):
        self.logger = logger
        self.module_list = []

    def get_module_name(self):
        return os.path.basename(os.getcwd())

    def is_module_disabled(self, db, module_name):
        return db.getSettings(f"{module_name}_disabled", "0") == "1"

    def load_modules(self, noLog=False):
        if not noLog:
            self.logger.info(f"<green>🔍 Loading modules ...</green>")

        if not os.path.exists("modules"):
            if not noLog:
                self.logger.info(f"<yellow>📁 Creating modules directory ...</yellow>")
            os.makedirs("modules")

        modules = os.listdir("modules")
        apiObj = api.API(self.logger)

        db = database.Database("database.db", self.logger)
        license = db.getSettings("license", "Free License")

        license_modules = apiObj.get_user_modules(license)
        if not license_modules or "error" in license_modules:
            license_modules = []

        for module in modules:
            if os.path.isdir(f"modules/{module}"):
                if not os.listdir(f"modules/{module}"):
                    continue

                if not os.path.exists(f"modules/{module}/bot.py"):
                    if not noLog:
                        self.logger.warning(
                            f"<yellow>└─ ⚠️ {module} bot.py not found!</yellow>"
                        )
                    continue

                commit_hash = None
                module_found = False
                for l_module in license_modules:
                    if l_module["name"] == module:
                        if not l_module["enabled"]:
                            if not noLog:
                                self.logger.warning(
                                    f"<yellow>└─ ⚠️ {module} is disabled in license!</yellow>"
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
                                f"<green>└─ ✅ <cyan>{module}</cyan> is up to date!</green>"
                            )
                if not module_found and not noLog:
                    self.logger.warning(
                        f"<yellow>└─ ⚠️ <cyan>{module}</cyan> is unverified!</yellow>"
                    )

                self.module_list.append(module)
                if not noLog:
                    self.logger.info(
                        f"<green>└─ ✅ <cyan>{module}</cyan> loaded!</green>"
                    )

        if not noLog:
            self.logger.info(
                f"✅ <cyan>{len(self.module_list)}</cyan> <green>modules loaded!</green>"
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
