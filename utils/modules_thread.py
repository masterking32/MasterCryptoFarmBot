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
    def __init__(self, logger):
        self.logger = logger
        self.api = api.API(self.logger)
        self.running_modules = []

    def getModules(self, Update=False):
        if not os.path.exists("modules"):
            return []

        modules = os.listdir("modules")

        db = database.Database("database.db", self.logger)
        license = db.getSettings("license", "Free License")

        license_modules = None
        if license != "Free License" and Update:
            license_modules = self.api.get_user_modules(license)

        if license_modules is None or "error" in license_modules:
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

            mcf_version = self.api.get_mcf_version()
            if mcf_version is None or "commit_hash" not in mcf_version:
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

        time.sleep(update_check_interval)

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

                        self.RestartModule(module["name"])

                self.logger.info(f"{lc.g}└─ ✅ Update check completed!{lc.rs}")
                time.sleep(update_check_interval)
            except Exception as e:
                self.logger.error(f"UpdateCheckThread: {e}")
                time.sleep(update_check_interval)

    def GetPythonExecutable(self):
        try:
            if os.name == "nt":
                # Windows
                return "python"
            elif os.name == "posix":
                # POSIX-compliant (Linux, MacOS, Termux)
                possible_paths = [
                    "/data/data/com.termux/files/usr/bin/python",
                    "/usr/local/bin/python3",
                    "/usr/bin/python3",
                    "/bin/python3",
                    "/usr/local/bin/python",
                    "/usr/bin/python",
                    "/bin/python",
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        return path
                return "python3"
            elif os.name == "java":
                # Jython
                return "jython"
            elif os.name == "os2":
                # OS/2
                return "python"
            elif os.name == "ce":
                # Windows CE
                return "python"
            elif os.name == "riscos":
                # RISC OS
                return "python"
            else:
                # Default fallback
                return "python3"
        except Exception as e:
            self.logger.error(f"GetPythonExecutable: {e}")
            return "python3"

    def RunModule(self, module):
        try:
            if not os.path.exists(f"modules/{module}/bot.py"):
                self.logger.error(f"{lc.r}❌ {module} module not found!{lc.rs}")
                return

            for running_module in self.running_modules:
                if running_module["module"] == module and running_module["is_running"]:
                    self.logger.warning(
                        f"{lc.y}🚀 {module} module is already running!{lc.rs}"
                    )
                    return

            self.logger.info(
                f"{lc.g}🚀 Running {lc.rs + lc.c}{module}{lc.rs + lc.g} module ...{lc.rs}"
            )
            python_executable = self.GetPythonExecutable()

            display_module_logs_in_console = utils.getConfig(
                config.config, "display_module_logs_in_console", False
            )
            display_module_log_cmd = ""
            if not display_module_logs_in_console:
                display_module_log_cmd = (
                    " >nul 2>nul" if os.name == "nt" else " >/dev/null 2>&1"
                )

            exec_command = (
                f'{python_executable} "modules/{module}/bot.py"{display_module_log_cmd}'
            )

            process = subprocess.Popen(exec_command, shell=True)
            module_data = {
                "module": module,
                "process": process,
                "command": exec_command,
                "is_running": True,
            }

            self.running_modules.append(module_data)
        except Exception as e:
            self.logger.error(f"RunModule: {e}")

    def StopModule(self, module):
        try:
            module_data = None
            for running_module in self.running_modules:
                if running_module["module"] == module and running_module["is_running"]:
                    module_data = running_module
                    break

            if module_data is None:
                self.logger.error(f"{lc.r}❌ {module} module not running!{lc.rs}")
                return

            self.logger.info(f"{lc.g}🚀 Stopping {module} module ...{lc.rs}")

            pid = module_data["process"].pid
            process = psutil.Process(pid)
            for child in process.children(recursive=True):
                child.kill()
            process.kill()

            module_data["is_running"] = False
            self.logger.info(f"{lc.g}🚀 {module} module stopped!{lc.rs}")

        except Exception as e:
            self.logger.error(f"StopModule: {e}")

    def RestartModule(self, module):
        try:
            if not os.path.exists(f"modules/{module}/bot.py"):
                self.logger.error(f"{lc.r}❌ {module} module not found!{lc.rs}")
                return

            self.logger.info(f"{lc.g}🚀 Restarting {module} module ...{lc.rs}")
            for running_module in self.running_modules:
                if running_module["module"] == module and running_module["is_running"]:
                    self.StopModule(module)
                    break

            self.RunModule(module)
        except Exception as e:
            self.logger.error(f"RestartModule: {e}")

    def RunAllModules(self):
        run_delay = utils.getConfig(config.config, "run_delay", 60)
        self.logger.info(
            f"{lc.g}🚀 Launching all modules in {lc.rs + lc.c}{run_delay}{lc.rs + lc.g} seconds...{lc.rs}"
        )
        time.sleep(run_delay)
        try:
            self.logger.info(f"{lc.g}🚀 Running all modules ...{lc.rs}")
            modules = self.getModules()
            for module in modules:
                if module["disabled"]:
                    self.logger.warning(
                        f"{lc.y}└─ ⚠️ {lc.rs + lc.c}{module['name']}{lc.rs + lc.y} is disabled!{lc.rs}"
                    )
                    continue

                self.RunModule(module["name"])

            self.logger.info(
                f"✅ {lc.c}{len(self.running_modules)}{lc.rs + lc.g} modules running!{lc.rs}"
            )
        except Exception as e:
            self.logger.error(f"RunAllModules: {e}")
            self.logger.info(f"{lc.r}🛑 Bot is stopping ... {lc.rs}")
