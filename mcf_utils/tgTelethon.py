# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import asyncio
import json
import os
import random
import time
import requests
import socks

from telethon.sync import TelegramClient
from telethon import functions, types
from telethon.tl.types import InputBotAppShortName, InputPeerNotifySettings
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest

from urllib.parse import unquote
from mcf_utils.utils import (
    get_random_name,
    testProxy,
    telethon_proxy,
    text_to_username,
    get_random_emoji,
    getConfig,
)
from contextlib import asynccontextmanager


@asynccontextmanager
async def connect_telethon(log, bot_globals, accountName, proxy=None):
    tgClient = None
    try:
        log.info(
            f"<green>🌍 Connecting to Telethon <c>({accountName})</c> session ...</green>"
        )

        if proxy and not testProxy(proxy):
            log.info(
                f"<yellow>❌ Proxy is not working for <c>{accountName}</c> session!</yellow>"
            )
            yield None
            return

        file_path = os.path.join(
            bot_globals["mcf_dir"], "telegram_accounts", f"{accountName}.session"
        )

        tgClient = TelegramClient(
            session=file_path,
            api_id=bot_globals["telegram_api_id"],
            api_hash=bot_globals["telegram_api_hash"],
            proxy=telethon_proxy(proxy) if proxy else None,
            auto_reconnect=False,
            device_model="Desktop (MCF-T)",
        )

        isConnected = await tgClient.connect()
        if not await tgClient.is_user_authorized():
            log.info(
                f"<yellow>❌ Telethon session <c>{accountName}</c> is not authorized!</yellow>"
            )
            yield None
            return

        if tgClient.is_connected():
            log.info(
                f"<green>✔️ Telethon session <c>{accountName}</c> has been connected successfully!</green>"
            )

            try:
                await tgClient(functions.account.UpdateStatusRequest(offline=False))
            except Exception as e:
                pass

            yield tgClient
        else:
            log.info(
                f"<yellow>❌ Telethon session <c>{accountName}</c> failed to connect!</yellow>"
            )
            yield None
    except Exception as e:
        try:
            if "database is locked" in str(e):
                log.info(
                    f"<y>🟡 It looks like the Telethon session <c>{accountName}</c> is busy with another module. Waiting for 30 seconds before retrying.</y>"
                )
                await asyncio.sleep(30)
                async with connect_telethon(
                    log, bot_globals, accountName, proxy
                ) as client:
                    yield client
                return
            else:
                log.info(
                    f"<yellow>❌ Telethon session <c>{accountName}</c> failed to connect!</yellow>"
                )
                log.error(f"<red>❌ {e}</red>")
            yield None
        except Exception as e:
            log.error(f"<red>❌ {e}</red>")
            yield None
    finally:
        try:
            if tgClient is not None and tgClient.is_connected():
                log.info(
                    f"<g>💻 Disconnecting Telethon session <c>{accountName}</c> ...</g>"
                )
                try:
                    await tgClient(functions.account.UpdateStatusRequest(offline=True))
                except Exception as e:
                    pass

                await tgClient.disconnect()
        except Exception as e:
            # self.log.error(f"<red>└─ ❌ {e}</red>")
            pass

        log.info(
            f"<green>✔️ Telethon session <c>{accountName}</c> has been disconnected successfully!</green>"
        )


class tgTelethon:
    def __init__(
        self,
        bot_globals=None,
        log=None,
        accountName=None,
        proxy=None,
        BotID=None,
        ReferralToken=None,
        ShortAppName=None,
        AppURL=None,
        MuteBot=False,
    ):
        self.bot_globals = bot_globals
        self.log = log
        self.accountName = accountName
        self.proxy = proxy
        self.BotID = BotID
        self.ShortAppName = ShortAppName
        self.ReferralToken = ReferralToken
        self.AppURL = AppURL
        self.MuteBot = MuteBot

    async def run(self):
        try:
            self.log.info(f"<green>🤖 Running {self.accountName} account ...</green>")
            async with connect_telethon(
                self.log, self.bot_globals, self.accountName, self.proxy
            ) as tgClient:
                if tgClient is None:
                    return None

                await self._account_setup(tgClient)
                return await self._get_web_view_data(tgClient)
        except Exception as e:
            self.log.info(
                f"<yellow>❌ Failed to run {self.accountName} account!</yellow>"
            )
            self.log.error(f"<red>❌ {e}</red>")
            return None

    async def accountSetup(self):
        async with connect_telethon(
            self.log, self.bot_globals, self.accountName, self.proxy
        ) as tgClient:
            if tgClient is None:
                self.log.info(
                    f"<y>└─ ❌ Account {self.accountName} session is not connected!</y>"
                )
                return None
            return await self._account_setup(tgClient)

    async def joinChat(self, url, noLog=False, mute=True):
        try:
            async with connect_telethon(
                self.log, self.bot_globals, self.accountName, self.proxy
            ) as tgClient:
                if tgClient is None:
                    return None
                return await self._join_chat(tgClient, url, noLog, mute)
        except Exception as e:
            self.log.info(
                f"<y>└─ ❌ Account {self.accountName} session is not connected!</y>"
            )
            self.log.error(f"<red>❌ {e}</red>")
            return None

    async def getMe(self):
        async with connect_telethon(
            self.log, self.bot_globals, self.accountName, self.proxy
        ) as tgClient:
            if tgClient is None:
                self.log.info(
                    f"<yellow>└─ ❌ Account {self.accountName} session is not connected!</yellow>"
                )
                return None
            return await self._get_me(tgClient)

    def getTGWebQuery(self, url):
        if not url or "first_name" not in url:
            return None
        if "tgWebAppData=" not in url:
            return url
        return unquote(
            url.split("tgWebAppData=", maxsplit=1)[1].split(
                "&tgWebAppVersion", maxsplit=1
            )[0]
        )

    async def getWebViewData(self):
        async with connect_telethon(
            self.log, self.bot_globals, self.accountName, self.proxy
        ) as tgClient:
            if tgClient is None:
                self.log.info(
                    f"<yellow>└─ ❌ Account {self.accountName} session is not connected!</yellow>"
                )
                return None
            return await self._get_web_view_data(tgClient)

    async def setName(self, firstName, lastName=None):
        async with connect_telethon(
            self.log, self.bot_globals, self.accountName, self.proxy
        ) as tgClient:
            if tgClient is None:
                self.log.info(
                    f"<y>└─ ❌ Account {self.accountName} session is not connected!</y>"
                )
                return None
            return await self._set_name(tgClient, firstName, lastName)

    async def _get_bot_app_link(self, tgClient, retry=0):
        try:
            if retry > 1:
                return None

            messages = await tgClient.get_messages(self.BotID, limit=5)
            if not messages or messages.total < 1:
                await self._send_start_bot(tgClient)
                await asyncio.sleep(3)

            if self.AppURL:
                return self.AppURL

            if self.ShortAppName:
                return None

            for message in messages:
                if not message.reply_markup:
                    continue

                webAppURL = None
                try:
                    if message.reply_markup.rows:
                        for row in message.reply_markup.rows:
                            for button in row.buttons:
                                if button.__class__.__name__ == "KeyboardButtonWebView":
                                    if button.url is None:
                                        continue

                                    webAppURL = button.url
                                    break

                    if webAppURL is None:
                        continue

                    return webAppURL
                except Exception as e:
                    self.log.error(f"<red>└─ ❌ {e}</red>")
                    continue
        except Exception as e:
            self.log.error(f"<red>└─ ❌ {e}</red>")

        await self._send_start_bot(tgClient)
        await asyncio.sleep(3)
        return await self._get_bot_app_link(tgClient, retry + 1)

    async def _send_start_bot(self, tgClient):
        self.log.info(
            f"<green>└─ 🤖 Sending start bot for {self.accountName} ...</green>"
        )

        try:
            await tgClient(
                functions.messages.StartBotRequest(
                    bot=self.BotID,
                    peer=self.BotID,
                    start_param=self.ReferralToken,
                )
            )

            await self._mute(tgClient, self.BotID)
        except Exception as e:
            self.log.error(
                f"<red>❌ failed to send start bot for {self.accountName}</red>"
            )
        return True

    async def _mute(self, tgClient, uID):
        try:
            chatObj = await tgClient.get_entity(uID)
            if chatObj is None:
                return True

            settings = InputPeerNotifySettings(
                silent=True,
                mute_until=int(time.time() + 10 * 365 * 24 * 60 * 60),
            )

            await tgClient(
                functions.account.UpdateNotifySettingsRequest(
                    peer=chatObj, settings=settings
                )
            )
            return True
        except Exception as e:
            return False

    async def _get_web_view_data(self, tgClient=None):
        try:
            app_url = await self._get_bot_app_link(tgClient)
            if not app_url and not self.ShortAppName:
                self.log.info(
                    f"<yellow>└─ ❌ {self.accountName} session failed to get app url!</yellow>"
                )
                return None

            result = None
            if self.ShortAppName:
                peer = await tgClient.get_input_entity(self.BotID)
                app = InputBotAppShortName(bot_id=peer, short_name=self.ShortAppName)
                result = await tgClient(
                    functions.messages.RequestAppWebViewRequest(
                        peer=peer,
                        app=app,
                        platform="android",
                        write_allowed=True,
                        compact=True,
                        start_param=self.ReferralToken,
                    )
                )
            elif app_url:
                result = await tgClient(
                    functions.messages.RequestWebViewRequest(
                        peer=self.BotID,
                        bot=self.BotID,
                        platform="android",
                        from_bot_menu=True,
                        url=app_url,
                        start_param=self.ReferralToken,
                    )
                )

            if not result:
                self.log.info(
                    f"<yellow>└─ ❌ {self.accountName} session failed to get web view data!</yellow>"
                )
                return None

            if not result.url:
                self.log.info(
                    f"<yellow>└─ ❌ {self.accountName} session failed to get web view data!</yellow>"
                )
                return None

            return result.url

        except Exception as e:
            self.log.info(
                f"<yellow>└─ ❌ {self.accountName} session failed to get web view data!</yellow>"
            )
            self.log.error(f"<red>❌ {e}</red>")
            return None

    async def _account_setup(self, tgClient):
        try:
            await self._join_chat(tgClient, "MasterCryptoFarmBot", True, False)
            UserAccount = await tgClient.get_me()
            fake_name = None
            if not UserAccount.username:
                self.log.info(
                    f"<green>└─ 🗿 Account username is empty. Setting a username for the account...</green>"
                )
                fake_name = await self._set_random_username(tgClient)
            self.log.info(
                f"<green>└─ ✅ Account {self.accountName} session is setup successfully!</green>"
            )

            if (
                self.bot_globals is None
                or "config" not in self.bot_globals
                or not getConfig(
                    self.bot_globals["config"], "auto_setup_accounts", False
                )
            ):
                return UserAccount

            if not UserAccount.last_name:
                await self._update_profile(
                    tgClient=tgClient,
                    first_name=UserAccount.first_name,
                    last_name=(
                        UserAccount.last_name or fake_name.split(" ")[-1]
                        if fake_name
                        else None
                    ),
                    bio=UserAccount.about or get_random_emoji(),
                )

            if not UserAccount.photo:
                tgClient.me = UserAccount
                await self._set_random_profile_photo(tgClient)

            UserAccount = await tgClient.get_me()
            return UserAccount
        except Exception as e:
            self.log.info(
                f"<y>└─ ❌ Account {self.accountName} session is not setup!</y>"
            )
            self.log.error(f"<red>└─ ❌ {e}</red>")
            return None

    async def _set_random_profile_photo(self, tgClient):
        try:
            self.log.info(
                f"<green>└─ 🗿 Setting profile photo for {self.accountName} session...</green>"
            )

            mcf_folder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            temp_folder = os.path.join(mcf_folder, "temp")
            file_path = os.path.join(temp_folder, f"{self.accountName}_avatar.png")

            try:
                avatar = requests.get(
                    "https://api.masterking32.com/mcf_bot/avatar_creator.php"
                )
                if avatar.status_code != 200:
                    self.log.info(
                        f"<yellow>└─ ❌ Failed to download avatar for {self.accountName} session!</yellow>"
                    )
                    return

                with open(file_path, "wb") as file:
                    file.write(avatar.content)
            except Exception as e:
                self.log.info(
                    f"<yellow>└─ ❌ Failed to download avatar for {self.accountName} session!</yellow>"
                )
                return

            file = await tgClient.upload_file(file_path)
            await tgClient(functions.photos.UploadProfilePhotoRequest(file=file))

            try:
                os.remove(file_path)
            except Exception as e:
                pass

            self.log.info(
                f"<green>└─ ✅ Account {self.accountName} session profile photo is set successfully!</green>"
            )
            return True

        except Exception as e:
            self.log.info(
                f"<yellow>└─ ❌ Failed to set session {self.accountName} profile photo!</yellow>"
            )
            self.log.error(f"<red>❌ {e}</red>")
            return False

    async def _update_profile(self, tgClient, first_name, last_name=None, bio=None):

        self.log.info(
            f"<green>└─ 🗿 Updating profile for {self.accountName} session...</green>"
        )
        try:
            if last_name is None:
                last_name = get_random_name()
                last_name = last_name.split(" ")[-1]
            update_profile_request = (
                UpdateProfileRequest(
                    first_name=first_name, last_name=last_name, about=bio
                )
                if bio
                else UpdateProfileRequest(first_name=first_name, last_name=last_name)
            )

            await tgClient(update_profile_request)

            self.log.info(
                f"<green>└─ ✅ Account {self.accountName} session last name is set successfully!</green>"
            )
            return True
        except Exception as e:
            self.log.info(
                f"<yellow>└─ ❌ Failed to set session {self.accountName} last name!</yellow>"
            )
            return False

    async def _set_random_username(self, tgClient):
        try:
            setUsername = False
            maxTries = 5
            RandomUsername = None
            faker_name = None
            while not setUsername and maxTries > 0:
                faker_name = get_random_name()
                RandomUsername = text_to_username(faker_name)
                self.log.info(
                    f"<green>└─ 🗿 Setting username for {self.accountName} session, New username <cyan>{RandomUsername}</cyan></green>"
                )
                setUsername = await tgClient(UpdateUsernameRequest(RandomUsername))
                maxTries -= 1
                await asyncio.sleep(5)

            return faker_name
        except Exception as e:
            self.log.info(
                f"<y>└─ ❌ Failed to set username for {self.accountName} session!</y>"
            )
            self.log.error(f"<red>❌ {e}</red>")
            return None

    async def _join_chat(self, tgClient, url, noLog=False, mute=True):
        if not noLog:
            self.log.info(f"<green>└─ 📰 Joining <cyan>{url}</cyan> ...</green>")
        try:
            chatObj = await tgClient.get_entity(url)
            if chatObj is None:
                if not noLog:
                    self.log.info(f"<y>└─ ❌ <cyan>{url}</cyan> not found!</y>")
                return False

            await tgClient(functions.channels.JoinChannelRequest(chatObj))
            if mute:
                await self._mute(tgClient, chatObj)

            if not noLog:
                self.log.info(
                    f"<green>└─ ✅ <cyan>{url}</cyan> has been joined successfully!</green>"
                )
            return True

        except Exception as e:
            if not noLog:
                self.log.info(f"<y>└─ ❌ </y><cyan>{url}</cyan><y> failed to join!</y>")
                self.log.error(f"<red>❌ {e}</red>")
        return False

    async def _set_name(self, tgClient, firstName, lastName=None):
        try:
            tgMe = await tgClient.get_me()
            await self._update_profile(
                tgClient=tgClient,
                first_name=firstName or tgMe.first_name,
                last_name=lastName or tgMe.last_name,
            )
            self.log.info(
                f"<green>└─ ✅ Account {self.accountName} session name is set successfully!</green>"
            )
            return True
        except Exception as e:
            self.log.info(
                f"<yellow>└─ ❌ Failed to set session {self.accountName} name!</yellow>"
            )
            return False

    async def _get_me(self, tgClient):
        try:
            return await tgClient.get_me()
        except Exception as e:
            self.log.info(
                f"<yellow>└─ ❌ Failed to get session {self.accountName} info!</yellow>"
            )
            return None
