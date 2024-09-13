# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

from flask import json
import utils.logColors as lc
from pyrogram import Client
import os
import asyncio

try:
    from config import config
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

    API_ID = config["telegram_api"]["api_id"]
    API_HASH = config["telegram_api"]["api_hash"]

    if not API_ID or not API_HASH:
        raise ValueError("API_ID and API_HASH not found in the .env file.")

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


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(register_sessions())
