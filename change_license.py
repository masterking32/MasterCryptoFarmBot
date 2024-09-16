# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import sqlite3
import utils.logColors as lc


def change_license(license: str) -> None:
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE settings SET value = ? WHERE name = 'license'", (license,)
        )
        conn.commit()
        conn.close()
        print(f"{lc.g}License changed successfully!{lc.rs}")
    except Exception as e:
        print(f"{lc.r}Error changing license!{lc.rs}")
        print(f"{lc.r}{e}{lc.rs}")


def main():
    license = input(f"\n{lc.g}Enter the new license: {lc.rs}")
    change_license(license)


if __name__ == "__main__":
    main()
