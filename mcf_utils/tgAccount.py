# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

from mcf_utils.utils import get_session_type
import os


class tgAccount:
    def __new__(cls, *args, **kwargs):
        log = None
        try:
            bot_globals = kwargs.get("bot_globals")
            account_name = kwargs.get("accountName")
            log = kwargs.get("log")
            if not bot_globals or not account_name or not log:
                from mcf_utils.tgTelethon import tgTelethon

                return tgTelethon(*args, **kwargs)

            mcf_dir = bot_globals.get("mcf_dir")

            session_type = cls.check_session(log, mcf_dir, account_name)
            if not session_type or session_type == "telethon":
                from mcf_utils.tgTelethon import tgTelethon

                return tgTelethon(*args, **kwargs)
            elif session_type == "pyrogram":
                from mcf_utils.tgPyrogram import tgPyrogram

                return tgPyrogram(*args, **kwargs)
        except Exception as e:
            if log:
                log.error(f"<red>Error: {e}</red>")
            else:
                print(f"Error: {e}")

        try:
            from mcf_utils.tgTelethon import tgTelethon

            return tgTelethon(*args, **kwargs)
        except Exception as e:
            if log:
                log.error(f"<red>Error: {e}</red>")
            else:
                print(f"Error: {e}")

    @staticmethod
    def check_session(log, mcf_dir, session_name):
        if not session_name:
            return "telethon"

        session_file = os.path.join(
            mcf_dir, "telegram_accounts", f"{session_name}.session"
        )

        if not os.path.exists(session_file):
            return "telethon"

        return get_session_type(log, session_file)
