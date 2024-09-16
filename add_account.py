# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import json
import utils.logColors as lc
from pyrogram import Client
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


async def register_sessions() -> None:
    if not os.path.exists("telegram_accounts"):
        os.mkdir("telegram_accounts")

    session_name = input(
        f"\n{lc.g}Enter a Name for account (press Enter to exit): {lc.rs}"
    )

    if not session_name.isalnum():
        print(
            f"\n{lc.r}Invalid session name! Only alphanumeric characters are allowed.{lc.rs}"
        )
        return None

    if not session_name:
        return None

    if os.path.exists(f"telegram_accounts/{session_name}.session"):
        print(f"\n{lc.r}Session already exists!{lc.rs}")
        return None

    phone_number = input(
        f"\n{lc.g}Enter the phone number of the account: {lc.rs}{lc.c}(e.g. +1234567890){lc.rs}: "
    )

    if not phone_number:
        print(f"\n{lc.r}Phone number is required!{lc.rs}")
        return None

    if not phone_number.startswith("+"):
        print(f"\n{lc.r}Phone number must start with '+'!{lc.rs}")
        return None

    if not phone_number.replace("+", "").isdigit():
        print(f"\n{lc.r}Phone number must contain only digits!{lc.rs}")
        return None

    session = Client(
        name=session_name,
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number=phone_number,
        workdir="telegram_accounts/",
    )

    async with session:
        user_data = await session.get_me()

    account = {
        "session_name": session_name,
        "phone_number": phone_number,
        "id": user_data.id,
        "first_name": user_data.first_name,
        "username": user_data.username,
        "disabled": False,
        "user_agent": "",
        "proxy": "",
    }

    accounts = []
    if os.path.exists("telegram_accounts/accounts.json"):
        with open("telegram_accounts/accounts.json", "r") as f:
            accounts = json.load(f)

    accounts.append(account)

    with open("telegram_accounts/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    print(f"\n{lc.y}User Information:{lc.rs}")
    print(f"{lc.y}ID: {lc.rs}{user_data.id}")
    print(f"{lc.y}Name: {lc.rs}{user_data.first_name}")
    print(f"{lc.y}Username: {lc.rs}{user_data.username}")
    print(f"{lc.y}Phone Number: {lc.rs}{user_data.phone_number}")
    print(f"{lc.y}Session Name: {lc.rs}{session_name}")

    print(f"\n{lc.g}Session created successfully!{lc.rs}")
    return session_name


async def import_sessions() -> None:
    if not os.path.exists("telegram_accounts"):
        return print(f"\n{lc.r}telegram_accounts folder does not exist!{lc.rs}")
    session_files = [
        f
        for f in os.listdir("telegram_accounts")
        if f.endswith(".session")
        and os.path.isfile(os.path.join("telegram_accounts", f))
    ]
    print(f"\n{lc.y}Found {len(session_files)} session files.{lc.rs}")
    if not session_files:
        return print(f"\n{lc.r}No session files found!{lc.rs}")
    for session_file in session_files:
        print(f"{lc.y}Importing {session_file}...{lc.rs}")
        session_name = session_file.replace(".session", "")
        if os.path.exists("telegram_accounts/accounts.json"):
            with open("telegram_accounts/accounts.json", "r") as f:
                accounts = json.load(f)
            if any(account["session_name"] == session_name for account in accounts):
                print(f"{lc.r}Session {session_name} already exists!{lc.rs}")
                continue
        session = Client(
            name=str(session_name),
            api_id=API_ID,
            api_hash=API_HASH,
            workdir="telegram_accounts/",
        )
        async with session:
            user_data = await session.get_me()
        account = {
            "session_name": session_name,
            "phone_number": user_data.phone_number,
            "id": user_data.id,
            "first_name": user_data.first_name,
            "username": user_data.username,
            "disabled": False,
            "user_agent": "",
            "proxy": "",
        }
        accounts = []
        if os.path.exists("telegram_accounts/accounts.json"):
            with open("telegram_accounts/accounts.json", "r") as f:
                accounts = json.load(f)
        accounts.append(account)
        with open("telegram_accounts/accounts.json", "w") as f:
            json.dump(accounts, f, indent=2)
        print(f"{lc.g}Session {session_name} imported successfully!{lc.rs}")


if __name__ == "__main__":
    print(
        f"{lc.y}Welcome to MasterCryptoFarmBot Telegram Account Manager!{lc.rs}\n"
        f"{lc.y}Please select an option:{lc.rs}"
        f"\n{lc.g}1. Register new sessions{lc.rs}"
        f"\n{lc.g}2. Import existing sessions{lc.rs}"
        f"\n{lc.g}3. Exit{lc.rs}"
        f"\n{lc.y}Enter your choice: {lc.rs}"
    )

    choice = input()

    if choice == "1":
        asyncio.get_event_loop().run_until_complete(register_sessions())

    elif choice == "2":
        asyncio.get_event_loop().run_until_complete(import_sessions())
    else:
        print(f"\n{lc.r}Closing...{lc.rs}")
        exit()
