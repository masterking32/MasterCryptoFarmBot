# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import os

import utils.logColors as lc


class Module:
    def __init__(self, logger):
        self.logger = logger
        self.module_list = []

    def get_ModuleName(self):
        return os.path.basename(os.getcwd())

    def is_module_disabled(self, db, module_name):
        return db.getSettings(f"{module_name}_disabled", "0") == "1"

    def load_modules(self):
        self.logger.info(f"{lc.g}🔍 Loading modules ...{lc.rs}")

        if not os.path.exists("modules"):
            self.logger.info(f"{lc.y}📁 Creating modules directory ...{lc.rs}")
            os.makedirs("modules")

        modules = os.listdir("modules")

        for module in modules:
            if os.path.isdir(f"modules/{module}"):
                if not os.listdir(f"modules/{module}"):
                    continue

                if not os.path.exists(f"modules/{module}/bot.py"):
                    self.logger.warning(f"{lc.y}└─ ⚠️ {module} bot.py not found!{lc.rs}")
                    continue

                self.module_list.append(module)
                self.logger.info(f"{lc.g}└─ 🔍 Loading {module} ...{lc.rs}")

        self.logger.info(
            f"✅ {lc.c}{len(self.module_list)}{lc.rs + lc.g} modules loaded!{lc.rs}"
        )
