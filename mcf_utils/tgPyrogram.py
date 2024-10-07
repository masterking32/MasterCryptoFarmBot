# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import asyncio
import os
import random
import time
import requests


from pyrogram import Client
from pyrogram.raw.types import (
    InputBotAppShortName,
    InputNotifyPeer,
    InputPeerNotifySettings,
)
from pyrogram.raw import functions
from pyrogram.raw.functions.messages import RequestWebView, RequestAppWebView
from pyrogram.raw.functions.account import UpdateNotifySettings
from mcf_utils.utils import (
    get_random_name,
    testProxy,
    parseProxy,
    text_to_username,
    get_random_emoji,
    getConfig,
)
from contextlib import asynccontextmanager


@asynccontextmanager
async def connect_pyrogram(log, bot_globals, accountName, proxy=None, retries=3):
    tgClient = None
    try:
        if retries < 0:
            log.info(
                f"<yellow>❌ Pyrogram session <c>{accountName}</c> failed to connect!</yellow>"
            )
            yield None
            return

        log.info(
            f"<green>🌍 Connecting to Pyrogram <c>({accountName})</c> session ...</green>"
        )

        if proxy and not testProxy(proxy):
            log.info(
                f"<yellow>❌ Proxy is not working for <c>{accountName}</c> session!</yellow>"
            )
            yield None
            return

        tgClient = Client(
            name=accountName,
            api_id=bot_globals["telegram_api_id"],
            api_hash=bot_globals["telegram_api_hash"],
            workdir=bot_globals["mcf_dir"] + "/telegram_accounts",
            plugins=dict(root="bot/plugins"),
            device_model="Desktop (MCF-P)",
            proxy=parseProxy(proxy) if proxy else None,
        )

        isConnected = False
        try:
            log.info(
                f"<green>🌍 Attempting to connect <c>{accountName}</c> ...</green>"
            )
            isConnected = await asyncio.wait_for(tgClient.connect(), 120)
        except asyncio.TimeoutError:
            log.info(
                f"<yellow>❌ Pyrogram session <c>{accountName}</c> timed out while connecting!</yellow>"
            )
            yield None
            return
        except asyncio.CancelledError:
            log.info(
                f"<yellow>❌ Pyrogram session <c>{accountName}</c> connection has been cancelled!</yellow>"
            )
            yield None
            return
        except Exception as e:
            log.info(
                f"<yellow>❌ Pyrogram session <c>{accountName}</c> failed to connect!</yellow>"
            )
            log.error(f"<red>❌ {e}</red>")
            yield None
            return

        if isConnected:
            log.info(
                f"<green>🌍 Pyrogram Session <c>{accountName}</c> connected successfully!</green>"
            )
            try:
                await tgClient.invoke(functions.account.UpdateStatus(offline=False))
            except Exception as e:
                pass
            yield tgClient
        else:
            yield None
    except Exception as e:
        try:
            if "database is locked" in str(e):
                log.info(
                    f"<y>🟡 It looks like the Pyrogram session <c>{accountName}</c> is busy with another module. Waiting for 30 seconds before retrying.</y>"
                )
                await asyncio.sleep(30)
                async with connect_pyrogram(
                    log, bot_globals, accountName, proxy, retries=retries - 1
                ) as client:
                    yield client
                return
            else:
                log.info(
                    f"<yellow>❌ Pyrogram session <c>{accountName}</c> failed to connect!</yellow>"
                )
                log.error(f"<red>❌ {e}</red>")
            yield None
        except Exception as e:
            log.error(f"<red>❌ {e}</red>")
            yield None

    except asyncio.CancelledError:
        log.info(
            f"<yellow>❌ Pyrogram session <c>{accountName}</c> connection has been cancelled!</yellow>"
        )
        yield None
    finally:
        try:
            log.info(
                f"<g>💻 Disconnecting Pyrogram session <c>{accountName}</c> ...</g>"
            )
            if tgClient is not None and tgClient.is_connected:
                try:
                    await tgClient.invoke(functions.account.UpdateStatus(offline=True))
                except Exception as e:
                    pass

                await tgClient.disconnect()
                log.info(
                    f"<green>✔️ Pyrogram session <c>{accountName}</c> has been disconnected successfully!</green>"
                )
        except Exception as e:
            # self.log.error(f"<red>└─ ❌ {e}</red>")
            pass


class tgPyrogram:
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
        self.NewStart = False  # Change to True if /start sent to bot

    async def run(self):
        try:
            self.log.info(f"<green>🤖 Running {self.accountName} account ...</green>")
            async with connect_pyrogram(
                self.log, self.bot_globals, self.accountName, self.proxy
            ) as tgClient:
                if tgClient is None:
                    return None

                await self._account_setup(tgClient)
                return await self._get_web_view_data(tgClient)
        except asyncio.CancelledError:
            self.log.info(
                f"<yellow>❌ Failed to run {self.accountName} account!</yellow>"
            )
            return None
        except Exception as e:
            self.log.info(
                f"<yellow>❌ Failed to run {self.accountName} account!</yellow>"
            )
            self.log.error(f"<red>❌ {e}</red>")
            return None

    async def getWebViewData(self):
        async with connect_pyrogram(
            self.log, self.bot_globals, self.accountName, self.proxy
        ) as tgClient:
            if tgClient is None:
                self.log.info(
                    f"<yellow>└─ ❌ Account {self.accountName} session is not connected!</yellow>"
                )
                return None
            return await self._get_web_view_data(tgClient)

    async def _get_bot_app_link(self, tgClient):
        try:
            BotID = self.BotID
            chatHistory = await tgClient.get_chat_history_count(BotID)
            if chatHistory < 1:
                await self.send_start_bot(tgClient)
                await asyncio.sleep(5)

            if self.AppURL:
                return self.AppURL

            if self.ShortAppName:
                return None

            async for message in tgClient.get_chat_history(BotID):
                if message is None:
                    continue

                isBot = message.from_user and message.from_user.is_bot
                if not isBot:
                    continue

                if not message.reply_markup:
                    continue

                webAppURL = None
                try:
                    if (
                        message.reply_markup.__class__.__name__
                        == "InlineKeyboardMarkup"
                    ):
                        for row in message.reply_markup.inline_keyboard:
                            for button in row:
                                if button.web_app is None or button.web_app.url is None:
                                    continue

                                webAppURL = button.web_app.url
                                break
                    elif (
                        message.reply_markup.__class__.__name__ == "ReplyKeyboardMarkup"
                    ):
                        for row in message.reply_markup.keyboard:
                            for button in row:
                                if button.url is None:
                                    continue

                                webAppURL = button.url
                                break
                except Exception as e:
                    self.log.error(f"<red>└─ ❌ {e}</red>")
                    continue

                if webAppURL is None:
                    continue

                message_date = int(message.date.timestamp())
                time_now = int(time.time())
                a_week = 60 * 60 * 24 * 7
                if time_now - message_date > a_week:
                    await asyncio.sleep(5)
                    await self.send_start_bot(tgClient)
                    return await self.get_app_web_link(tgClient)

                return webAppURL
        except Exception as e:
            self.log.error(f"<red>└─ ❌ {e}</red>")

        return None

    async def send_start_bot(self, tgClient):
        self.log.info(
            f"<green>└─ 🤖 Sending start bot for {self.accountName} ...</green>"
        )

        self.NewStart = True

        peer = await tgClient.resolve_peer(self.BotID)
        await tgClient.invoke(
            functions.messages.StartBot(
                bot=peer,
                peer=peer,
                random_id=random.randint(100000, 999999),
                start_param=self.ReferralToken,
            )
        )

        return True

    async def _get_web_view_data(self, tgClient=None):
        try:
            BotID = self.BotID

            app_url = await self._get_bot_app_link(tgClient)

            if not app_url and not self.ShortAppName:
                self.log.info(
                    f"<yellow>└─ ❌ {self.accountName} session failed to get app url!</yellow>"
                )
                return None
            peer = await tgClient.resolve_peer(BotID)

            if self.MuteBot:
                try:
                    peerMute = InputNotifyPeer(peer=peer)
                    settings = InputPeerNotifySettings(
                        silent=True,
                        mute_until=int(time.time() + 10 * 365 * 24 * 60 * 60),
                    )
                    await tgClient.invoke(
                        UpdateNotifySettings(peer=peerMute, settings=settings)
                    )
                except Exception as e:
                    pass

            bot_app = (
                InputBotAppShortName(bot_id=peer, short_name=self.ShortAppName)
                if self.ShortAppName
                else None
            )

            web_view = await tgClient.invoke(
                RequestAppWebView(
                    peer=peer,
                    app=bot_app,
                    platform="android",
                    write_allowed=True,
                    start_param=self.ReferralToken if self.NewStart else "",
                )
                if bot_app
                else RequestWebView(
                    peer=peer,
                    bot=peer,
                    platform="android",
                    from_bot_menu=False,
                    url=app_url,
                )
            )

            if not web_view and "url" not in web_view:
                self.log.info(
                    f"<yellow>└─ ❌ {self.accountName} session failed to get web view data!</yellow>"
                )
                return None

            return web_view.url
        except Exception as e:
            self.log.info(
                f"<yellow>└─ ❌ {self.accountName} session failed to get web view data!</yellow>"
            )
            self.log.error(f"<red>❌ {e}</red>")
            return None

    async def accountSetup(self):
        async with connect_pyrogram(
            self.log, self.bot_globals, self.accountName, self.proxy
        ) as tgClient:
            if tgClient is None:
                self.log.info(
                    f"<y>└─ ❌ Account {self.accountName} session is not connected!</y>"
                )
                return None
            return await self._account_setup(tgClient)

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
                    lastName=(
                        UserAccount.last_name or fake_name.split(" ")[-1]
                        if fake_name
                        else None
                    ),
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

            await tgClient.set_profile_photo(photo=file_path)

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

    async def _update_profile(self, tgClient, first_name, lastName=None, bio=None):
        self.log.info(
            f"<green>└─ 🗿 Updating profile for {self.accountName} session...</green>"
        )
        try:
            if lastName is None:
                lastName = get_random_name()
                lastName = lastName.split(" ")[-1]
            await tgClient.update_profile(
                first_name=first_name, last_name=lastName, bio=bio or get_random_emoji()
            )

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
                # RandomUsername = "".join(
                #     random.choices(string.ascii_lowercase, k=random.randint(15, 30))
                # )
                faker_name = get_random_name()
                RandomUsername = text_to_username(faker_name)
                self.log.info(
                    f"<green>└─ 🗿 Setting username for {self.accountName} session, New username <cyan>{RandomUsername}</cyan></green>"
                )
                setUsername = await tgClient.set_username(RandomUsername)
                maxTries -= 1
                await asyncio.sleep(5)

            return faker_name
        except Exception as e:
            self.log.info(
                f"<y>└─ ❌ Failed to set username for {self.accountName} session!</y>"
            )
            self.log.error(f"<red>❌ {e}</red>")
            return None

    async def joinChat(self, url, noLog=False, mute=True):
        try:
            async with connect_pyrogram(
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

    async def _join_chat(self, tgClient, url, noLog=False, mute=True):
        if not noLog:
            self.log.info(f"<green>└─ 📰 Joining <cyan>{url}</cyan> ...</green>")
        try:
            chatObj = await tgClient.join_chat(url)
            if chatObj and chatObj.id:
                if mute:
                    peer = InputNotifyPeer(peer=await tgClient.resolve_peer(chatObj.id))
                    settings = InputPeerNotifySettings(
                        silent=True,
                        mute_until=int(time.time() + 10 * 365 * 24 * 60 * 60),
                    )
                    await tgClient.invoke(
                        UpdateNotifySettings(peer=peer, settings=settings)
                    )
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

    async def setName(self, firstName, lastName=None):
        async with connect_pyrogram(
            self.log, self.bot_globals, self.accountName, self.proxy
        ) as tgClient:
            if tgClient is None:
                self.log.info(
                    f"<y>└─ ❌ Account {self.accountName} session is not connected!</y>"
                )
                return None
            return await self._set_name(tgClient, firstName, lastName)

    async def _set_name(self, tgClient, firstName, lastName=None):
        try:
            tgMe = await tgClient.get_me()
            await tgClient.update_profile(
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

    async def getMe(self):
        async with connect_pyrogram(
            self.log, self.bot_globals, self.accountName, self.proxy
        ) as tgClient:
            if tgClient is None:
                self.log.info(
                    f"<yellow>└─ ❌ Account {self.accountName} session is not connected!</yellow>"
                )
                return None
            return await self._get_me(tgClient)

    async def _get_me(self, tgClient):
        try:
            return await tgClient.get_me()
        except Exception as e:
            self.log.info(
                f"<yellow>└─ ❌ Failed to get session {self.accountName} info!</yellow>"
            )
            return None
