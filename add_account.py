# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import json
import mcf_utils.logColors as lc
import mcf_utils.utils as utils
import os
import asyncio

try:
    from config import config

    API_ID = config["telegram_api"]["api_id"]
    API_HASH = config["telegram_api"]["api_hash"]
    if API_ID == 1234 or API_HASH == "":
        print(f"{lc.r}API_ID or API_HASH not found in the config.py file.{lc.rs}")
        raise ValueError("API_ID or API_HASH not found in the config.py file.")
except ImportError:
    print(
        f"{lc.r}Please create a config.py file with the required variables, check the example file (config.py.sample){lc.rs}"
    )
    raise ImportError(
        "Please create a config.py file with the required variables, check the example file (config.py.sample)"
    )


def add_account_to_json(account):
    accounts = []
    try:
        if os.path.exists("telegram_accounts/accounts.json"):
            with open("telegram_accounts/accounts.json", "r") as f:
                accounts = json.load(f)
                f.close()
    except Exception as e:
        accounts = []

    for acc in accounts:
        if acc["id"] == account["id"]:
            print(f"\n{lc.r}Account ID already exists!{lc.rs}")
            return None
        if acc["phone_number"] == account["phone_number"]:
            print(f"\n{lc.r}Phone number already exists!{lc.rs}")
            return None
        if acc["session_name"] == account["session_name"]:
            print(f"\n{lc.r}Session name already exists!{lc.rs}")
            return None

    accounts.append(account)

    try:
        with open("telegram_accounts/accounts.json", "w") as f:
            json.dump(accounts, f, indent=2)
            f.close()
    except Exception as e:
        print(f"\n{lc.r}Error while writing to accounts.json file!{lc.rs}")
        return None

    print(f"{lc.g}✅ Session created successfully!{lc.rs}")
    return account["session_name"]


async def get_sesstion_name() -> str:
    print(f"{lc.g}----------------------------------------------------{lc.rs}")
    print(
        f"{lc.y}🔤 Choose a name for the account (only alphanumeric characters are allowed). This will be used for the file name and logs.{lc.rs}"
    )
    session_name = input(
        f"\n{lc.g}📝 Enter a Name for account (press Enter to exit): {lc.rs}"
    )

    if not session_name:
        print(f"\n{lc.r}🚪 Exiting...{lc.rs}")
        exit()

    if not session_name.isalnum():
        print(
            f"\n{lc.r}❌ Invalid session name! Only alphanumeric characters are allowed.{lc.rs}"
        )
        return await register_sessions()

    if os.path.exists(f"telegram_accounts/{session_name}.session"):
        print(f"\n{lc.r}⚠️ Session already exists!{lc.rs}")
        print(
            f"\n{lc.r}🗑️ If you want to re-import, simply delete the session file manually! You can find it inside the telegram_accounts folder!{lc.rs}"
        )
        return await register_sessions()
    return session_name


async def get_lib_choice() -> str:
    print(f"{lc.g}----------------------------------------------------{lc.rs}")
    print(f"{lc.y}📚 Please select a library:{lc.rs}")
    print(f"{lc.g}1. Telethon (Recommended){lc.rs}")
    print(f"{lc.g}2. Pyrogram{lc.rs}")
    print(f"{lc.g}3. Exit{lc.rs}")

    choice = input(f"\n{lc.y}🔢 Enter your choice: {lc.rs}")
    if choice == "3":
        print(f"\n{lc.r}🚪 Closing...{lc.rs}")
        exit()

    if choice not in ["1", "2"]:
        return await get_lib_choice()
    return choice


async def register_telethon(session_name, phone_number) -> None:
    import telethon.sync
    from telethon.sync import TelegramClient

    session_path = f"telegram_accounts/{session_name}"
    tg_client = TelegramClient(
        session=session_path,
        api_id=API_ID,
        api_hash=API_HASH,
        device_model="Desktop (MCF-T)",
    )

    user_data = None
    try:
        await tg_client.connect()
        if not await tg_client.is_user_authorized():
            await tg_client.send_code_request(phone_number)
            code = input(f"\n{lc.g}🔑 Enter the verification code: {lc.rs}")
            try:
                await tg_client.sign_in(phone_number, code)
            except telethon.errors.SessionPasswordNeededError:
                password = input(f"\n{lc.g}🔒 Enter your 2FA password: {lc.rs}")
                await tg_client.sign_in(password=password)
            except Exception as e:
                try:
                    await tg_client.disconnect()
                except Exception as e:
                    pass

                os.remove(f"{session_path}.session")
                print(f"\n{lc.r}❌ Error: {e}{lc.rs}")
                return await getPhoneNumber(session_name, "1")

        user_data = await tg_client.get_me()
    except Exception as e:
        print(f"\n{lc.r}❌ Error: {e}{lc.rs}")

    try:
        await tg_client.disconnect()
    except Exception as e:
        pass

    if not user_data:
        os.remove(f"{session_path}.session")
        print(f"\n{lc.r}❌ Failed to create the session!{lc.rs}")
        return await getPhoneNumber(session_name, "1")

    account = {
        "session_name": session_name,
        "phone_number": user_data.phone,
        "id": user_data.id,
        "first_name": user_data.first_name,
        "username": user_data.username,
        "disabled": True,
        "user_agent": "",
        "proxy": "",
        "type": "telethon",
    }

    add_account_to_json(account)
    print(f"\n{lc.g}✅ Session created successfully!{lc.rs}")
    return session_name


async def register_pyrogram(session_name, phone_number) -> None:
    import pyrogram
    from pyrogram import Client

    session_path = f"telegram_accounts/{session_name}"
    session = Client(
        name=session_name,
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number=phone_number,
        workdir="telegram_accounts/",
    )

    user_data = None
    try:
        async with session:
            user_data = await session.get_me()
    except Exception as e:

        print(f"\n{lc.r}❌ Error: {e}{lc.rs}")
    try:
        await session.stop()
    except Exception as e:
        pass
    if not user_data:
        os.remove(f"{session_path}.session")
        print(f"\n{lc.r}❌ Failed to create the session!{lc.rs}")
        return await getPhoneNumber(session_name, "2")

    account = {
        "session_name": session_name,
        "phone_number": user_data.phone_number,
        "id": user_data.id,
        "first_name": user_data.first_name,
        "username": user_data.username,
        "disabled": True,
        "user_agent": "",
        "proxy": "",
        "type": "pyrogram",
    }

    add_account_to_json(account)
    print(f"\n{lc.g}✅ Session created successfully!{lc.rs}")
    return session_name


async def getPhoneNumber(session_name, lib_choice):
    phone_number = input(
        f"\n{lc.g}📞 Enter the phone number of the account: {lc.rs}{lc.c}(e.g. +1234567890){lc.rs}: "
    )

    if not phone_number:
        print(f"\n{lc.r}❌ Phone number is required!{lc.rs}")
        return await getPhoneNumber(session_name, lib_choice)

    if not phone_number.startswith("+"):
        print(f"\n{lc.r}❌ Phone number must start with '+'!{lc.rs}")
        return await getPhoneNumber(session_name, lib_choice)

    phone_number = phone_number.replace(" ", "")
    if not phone_number.replace("+", "").isdigit():
        print(f"\n{lc.r}❌ Phone number must contain only digits!{lc.rs}")
        return await getPhoneNumber(session_name, lib_choice)

    if lib_choice == "1":
        return await register_telethon(session_name, phone_number)
    elif lib_choice == "2":
        return await register_pyrogram(session_name, phone_number)

    print(f"\n{lc.r}❌ Invalid library choice!{lc.rs}")
    return await get_lib_choice()


async def register_sessions() -> None:
    session_name = await get_sesstion_name()
    print(f"\n{lc.y}Session Name: {lc.rs}{lc.c}{session_name}{lc.rs}")
    lib_choice = await get_lib_choice()
    await getPhoneNumber(session_name, lib_choice)

    await register_sessions()


async def check_pyrogram_session(session_name) -> bool:
    import pyrogram

    session = pyrogram.Client(
        name=session_name,
        api_id=API_ID,
        api_hash=API_HASH,
        workdir="telegram_accounts/",
    )

    try:
        await session.connect()
        user_data = await session.get_me()
        return user_data

    except Exception as e:
        print(f"\n{lc.r}❌ Error: {e}{lc.rs}")
        return False
    finally:
        try:
            await session.disconnect()
        except Exception as e:
            pass


async def check_telethon_session(session_name) -> bool:
    from telethon.sync import TelegramClient

    session_path = f"telegram_accounts/{session_name}"
    tg_client = TelegramClient(
        session=session_path,
        api_id=API_ID,
        api_hash=API_HASH,
        device_model="Desktop (MCF-T)",
    )

    user_data = None
    try:
        await tg_client.connect()
        if not await tg_client.is_user_authorized():
            await tg_client.disconnect()
            return False

        user_data = await tg_client.get_me()
    except Exception as e:
        print(f"\n{lc.r}❌ Error: {e}{lc.rs}")

    try:
        await tg_client.disconnect()
    except Exception as e:
        pass

    return user_data


async def import_sessions() -> None:
    session_files = [
        f
        for f in os.listdir("telegram_accounts")
        if f.endswith(".session")
        and os.path.isfile(os.path.join("telegram_accounts", f))
    ]

    print(f"\n{lc.y}🔍 Found {len(session_files)} session files.{lc.rs}")

    if not session_files:
        print(
            f"\n{lc.r}🗃️ Please copy your Pyrogram/Telethon session files into the 'telegram_accounts' folder.{lc.rs}"
        )
        return print(f"\n{lc.r}❌ No session files found!{lc.rs}")

    for session_file in session_files:
        try:
            print(f"{lc.y}📂 Importing {session_file}...{lc.rs}")
            if not session_file.endswith(".session"):
                print(f"{lc.r}❌ Invalid session file!{lc.rs}")
                continue

            clean_session_name = "".join(
                e for e in session_file.replace(".session", "") if e.isalnum()
            )

            if session_file != f"{clean_session_name}.session":
                if os.path.exists(f"telegram_accounts/{clean_session_name}.session"):
                    print(
                        f"{lc.r}⚠️ Session {clean_session_name} file already exists!{lc.rs}"
                    )
                    continue

                os.rename(
                    f"telegram_accounts/{session_file}",
                    f"telegram_accounts/{clean_session_name}.session",
                )

                session_file = f"{clean_session_name}.session"

            session_name = session_file.replace(".session", "")
            if os.path.exists("telegram_accounts/accounts.json"):
                accounts = []
                with open("telegram_accounts/accounts.json", "r") as f:
                    accounts = json.load(f)
                    f.close()
                if any(account["session_name"] == session_name for account in accounts):
                    print(f"{lc.r}⚠️ Session {session_name} already exists!{lc.rs}")
                    continue

            session_type = utils.get_session_type(
                None, f"telegram_accounts/{session_file}"
            )
            print(f"{lc.y}🔍 Session Type: {lc.rs}{lc.c}{session_type}{lc.rs}")

            user_data = None
            if session_type == "telethon":
                user_data = await check_telethon_session(session_name)
            elif session_type == "pyrogram":
                user_data = await check_pyrogram_session(session_name)

            if not user_data:
                print(f"{lc.r}❌ Failed to import the session!{lc.rs}")
                continue

            account = {
                "session_name": session_name,
                "phone_number": (
                    user_data.phone
                    if session_type == "telethon"
                    else user_data.phone_number
                ),
                "id": user_data.id,
                "first_name": user_data.first_name,
                "username": user_data.username,
                "disabled": True,
                "user_agent": "",
                "proxy": "",
                "type": session_type,
            }

            add_account_to_json(account)
        except Exception as e:
            print(f"{lc.r}❌ Error: {e}{lc.rs}")

    print(f"\n{lc.g}🎉 All sessions imported successfully!{lc.rs}")


if __name__ == "__main__":
    if not os.path.exists("telegram_accounts"):
        os.mkdir("telegram_accounts")
    print(
        f"{lc.c}👋 Welcome to MasterCryptoFarmBot Telegram Account Manager!{lc.rs}\n"
        f"{lc.g}----------------------------------------------------{lc.rs}\n"
        f"{lc.r}🚀 After creating a session, run main.py{lc.rs}\n"
        f"{lc.r}🛠️ Then go to Control Panel > Manage Accounts, set the User-Agent (Proxy is optional), and enable the account.{lc.rs}\n"
        f"{lc.r}🔒 By default, the accounts are disabled after creation and need to be enabled manually.{lc.rs}\n"
        f"{lc.g}----------------------------------------------------{lc.rs}\n"
        f"{lc.y}📋 Please select an option:{lc.rs}"
        f"\n{lc.g}1. 🆕 Register new sessions (PyroGram or Telethon){lc.rs}"
        f"\n{lc.g}2. 📂 Import existing sessions (PyroGram or Telethon session files){lc.rs}"
        f"\n{lc.g}3. ❌ Exit{lc.rs}"
        f"\n{lc.y}Enter your choice: {lc.rs}"
    )

    choice = input()

    if choice == "1":
        asyncio.run(register_sessions())

    elif choice == "2":
        asyncio.run(import_sessions())
    else:
        print(f"\n{lc.r}Closing...{lc.rs}")
        exit()
