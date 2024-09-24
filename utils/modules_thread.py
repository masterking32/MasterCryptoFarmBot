# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import os
import time
import subprocess
import psutil

import utils.logColors as lc
import utils.Git as Git
import utils.utils as utils
import utils.api as api
import utils.database as database
from utils.modules import Module
import config


class Module_Thread:
    MODULES_DIR = "modules"
    BOT_FILE = "bot.py"
    DEFAULT_LICENSE = "Free License"
    PYTHON_EXECUTABLES = [
        "/usr/local/bin/python3",
        "/usr/bin/python3",
        "/bin/python3",
        "/data/data/com.termux/files/usr/bin/python",
        "/usr/local/bin/python",
        "/usr/bin/python",
        "/bin/python",
    ]

    def __init__(self, logger):
        self.logger = logger
        self.api = api.API(self.logger)
        self.running_modules = []

    def get_modules(self, update=False):
        if not os.path.exists(self.MODULES_DIR):
            return []

        modules = os.listdir(self.MODULES_DIR)
        db = database.Database("database.db", self.logger)
        license = db.getSettings("license", self.DEFAULT_LICENSE)

        license_modules = self._fetch_license_modules(license, update)
        modules_output = []

        for module in modules:
            module_path = os.path.join(self.MODULES_DIR, module)
            if not os.path.isdir(module_path) or not os.path.exists(
                os.path.join(module_path, self.BOT_FILE)
            ):
                continue

            new_module = self._initialize_module(db, module, license_modules)
            if new_module["disabled"]:
                modules_output.append(new_module)
                continue

            try:
                self._update_module_if_required(new_module, module, update, db)
            except Exception as e:
                self.logger.error(f"Modules Thread: {e}")

            modules_output.append(new_module)

        return modules_output

    def _fetch_license_modules(self, license, update):
        if license != self.DEFAULT_LICENSE and update:
            license_modules = self.api.get_user_modules(license)
            if license_modules is None or "error" in license_modules:
                return []
            return license_modules
        return []

    def _initialize_module(self, db, module, license_modules):
        new_module = {
            "name": module,
            "commit_hash": None,
            "restart_required": False,
            "disabled": db.getSettings(f"{module}_disabled", "0") == "1",
        }

        for l_module in license_modules:
            if l_module["name"] == module:
                if not l_module["enabled"]:
                    new_module["disabled"] = True
                new_module["commit_hash"] = l_module["commit_hash"]
                break

        return new_module

    def _update_module_if_required(self, new_module, module, update, db):
        if not update:
            return

        git = Git.Git(self.logger, config.config)
        modules_class = Module(self.logger)

        if (
            utils.getConfig(config.config, "auto_update_modules", True)
            and new_module["commit_hash"] is not None
            and modules_class.UpdateRequired(module, new_module["commit_hash"])
        ):
            new_module["restart_required"] = True
            directory = os.path.join(os.getcwd(), f"{self.MODULES_DIR}/{module}")
            git.UpdateProject(directory, False)
            db.migration_modules([module])

    def check_main_project_update(self):
        try:
            if not utils.getConfig(config.config, "auto_update", True):
                return

            git = Git.Git(self.logger, config.config)
            local_git_commit = git.GetRecentLocalCommit()
            if local_git_commit is None:
                return

            mcf_version = self.api.get_mcf_version()
            if mcf_version is None or "commit_hash" not in mcf_version:
                return

            commit_hash = mcf_version["commit_hash"]

            if not git.GitHasCommit(commit_hash):
                self.logger.error("<red>🔄 Main Project is not updated ... </red>")
                git.UpdateProject()
                self.logger.error("<red>🔄 Please restart the bot ... </red>")
        except Exception as e:
            self.logger.error(f"CheckMainProjectUpdate: {e}")

    def update_check_thread(self):
        if not utils.getConfig(config.config, "auto_update_modules", True):
            return

        update_check_interval = max(
            utils.getConfig(config.config, "update_check_interval", 3600), 3600
        )
        time.sleep(update_check_interval)

        while True:
            self.logger.info("<green>🔄 Checking for updates ...</green>")
            self.check_main_project_update()
            try:
                modules = self.get_modules(update=True)
                for module in modules:
                    if module["restart_required"]:
                        self.logger.warning(
                            f"<yellow>└─ 🔄 Module Restart required for <cyan>{module['name']}</cyan> module ...</yellow>"
                        )
                        self.restart_module(module["name"])

                self.logger.info("<green>└─ ✅ Update check completed!</green>")
                time.sleep(update_check_interval)
            except Exception as e:
                self.logger.error(f"UpdateCheckThread: {e}")
                time.sleep(update_check_interval)

    def get_python_executable(self):
        try:
            if os.name == "nt":
                return "python"
            elif os.name == "posix":
                for path in self.PYTHON_EXECUTABLES:
                    if os.path.exists(path):
                        return path
                return "python3"
            elif os.name in ["java", "os2", "ce", "riscos"]:
                return "python"
            else:
                return "python3"
        except Exception as e:
            self.logger.error(f"GetPythonExecutable: {e}")
            return "python3"

    def run_module(self, module):
        try:
            module_path = os.path.join(self.MODULES_DIR, module, self.BOT_FILE)
            if not os.path.exists(module_path):
                self.logger.error(f"<red>❌ {module} module not found!</red>")
                return

            if any(
                rm["module"] == module and rm["is_running"]
                for rm in self.running_modules
            ):
                self.logger.warning(
                    f"<yellow>🚀 {module} module is already running!</yellow>"
                )
                return

            db = database.Database("database.db", self.logger)
            if db.getSettings(f"{module}_disabled", "0") == "1":
                self.logger.error(f"<red>❌ {module} module is disabled!</red>")
                return

            self.logger.info(
                f"<green>🚀 Running <cyan>{module}</cyan> module ...</green>"
            )
            python_executable = self.get_python_executable()

            display_module_logs_in_console = utils.getConfig(
                config.config, "display_module_logs_in_console", False
            )
            display_module_log_cmd = (
                ""
                if display_module_logs_in_console
                else (" >nul 2>nul" if os.name == "nt" else " >/dev/null 2>&1")
            )

            exec_command = (
                f'{python_executable} "{module_path}"{display_module_log_cmd}'
            )
            process = subprocess.Popen(exec_command, shell=True)
            self.running_modules.append(
                {
                    "module": module,
                    "process": process,
                    "command": exec_command,
                    "is_running": True,
                }
            )
        except Exception as e:
            self.logger.error(f"RunModule: {e}")

    def stop_module(self, module):
        try:
            module_data = next(
                (
                    rm
                    for rm in self.running_modules
                    if rm["module"] == module and rm["is_running"]
                ),
                None,
            )
            if module_data is None:
                self.logger.error(f"<red>❌ {module} module not running!</red>")
                return

            self.logger.info(f"<green>🚀 Stopping {module} module ...</green>")
            process = psutil.Process(module_data["process"].pid)
            for child in process.children(recursive=True):
                child.kill()
            process.kill()

            module_data["is_running"] = False
            self.logger.info(f"<green>🚀 {module} module stopped!</green>")
        except Exception as e:
            self.logger.error(f"StopModule: {e}")

    def restart_module(self, module):
        try:
            module_path = os.path.join(self.MODULES_DIR, module, self.BOT_FILE)
            if not os.path.exists(module_path):
                self.logger.error(f"<red>❌ {module} module not found!</red>")
                return

            self.logger.info(f"<green>🚀 Restarting {module} module ...</green>")
            self.stop_module(module)

            db = database.Database("database.db", self.logger)
            if not db.getSettings(f"{module}_disabled", "0") == "1":
                self.run_module(module)
        except Exception as e:
            self.logger.error(f"RestartModule: {e}")

    def run_all_modules(self):
        run_delay = utils.getConfig(config.config, "run_delay", 60)
        self.logger.info(
            f"<green>🚀 Launching all modules in <cyan>{run_delay}</cyan> seconds...</green>"
        )
        time.sleep(run_delay)
        try:
            self.logger.info(f"<green>🚀 Running all modules ...</green>")
            modules = self.get_modules()
            for module in modules:
                if module["disabled"]:
                    if any(
                        rm["module"] == module["name"] and rm["is_running"]
                        for rm in self.running_modules
                    ):
                        self.stop_module(module["name"])

                    self.logger.warning(
                        f"<yellow>└─ ⚠️ <cyan>{module['name']}</cyan> is disabled!</yellow>"
                    )
                    continue

                if not any(
                    rm["module"] == module["name"] and rm["is_running"]
                    for rm in self.running_modules
                ):
                    self.run_module(module["name"])

            self.logger.info(
                f"<green>✅ <cyan>{len(self.running_modules)}</cyan> modules running!</green>"
            )
        except Exception as e:
            self.logger.error(f"RunAllModules: {e}")
            self.logger.info("<red>🛑 Bot is stopping ... </red>")
