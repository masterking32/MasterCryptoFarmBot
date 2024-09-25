y  # Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import os
import sys
import random
import string
import time

from pyrogram import Client
from pyrogram.raw.types import (
    InputBotAppShortName,
    InputNotifyPeer,
    InputPeerNotifySettings,
)
from pyrogram.raw import functions
from pyrogram.raw.functions.messages import RequestWebView, RequestAppWebView
from pyrogram.raw.functions.account import UpdateNotifySettings
from urllib.parse import unquote
from utils.utils import testProxy, parseProxy


class tgAccount:
    def __init__(
        self,
        bot_globals,
        log,
        accountName,
        proxy,
        BotID,
        ReferralToken=None,
        ShortAppName=None,
        AppURL=None,
    ):
        self.bot_globals = bot_globals
        self.log = log
        self.accountName = accountName
        self.tgClient = None
        self.proxy = proxy
        self.BotID = BotID
        self.ShortAppName = ShortAppName
        self.ReferralToken = ReferralToken
        self.AppURL = AppURL

    async def Connect(self):
        if self.tgClient is not None and self.tgClient.is_connected:
            return self.tgClient

        if self.proxy and not testProxy(self.proxy):
            self.log.info(f"<red>└─ ❌ Proxy {self.proxy} is not working!</red>")
            return None

        self.tgClient = Client(
            name=self.accountName,
            api_id=self.bot_globals["telegram_api_id"],
            api_hash=self.bot_globals["telegram_api_hash"],
            workdir=self.bot_globals["mcf_dir"] + "/telegram_accounts",
            plugins=dict(root="bot/plugins"),
            proxy=parseProxy(self.proxy) if self.proxy else None,
        )

        self.log.info(f"<green>└─ 🌍 Connecting {self.accountName} session ...</green>")
        try:
            isConnected = await self.tgClient.connect()
            if isConnected:
                self.log.info(
                    f"<green>└─ 🌍 Session {self.accountName} connected successfully!</green>"
                )
                return self.tgClient
            else:
                return None
        except Exception as e:
            self.log.error(f"└─ ❌ {e}")
            return None

    async def run(self):
        try:
            self.log.info(f"<green>🤖 Running {self.accountName} account ...</green>")
            if not os.path.exists(
                self.bot_globals["mcf_dir"]
                + f"/telegram_accounts/{self.accountName}.session"
            ):
                self.log.info(
                    f"<yellow>❌ Account {self.accountName} session is not found!</yellow>"
                )
                return None

            self.log.info(
                f"<green>└─ 🔑 Loading {self.accountName} session ...</green>"
            )

            tgClient = await self.Connect()
            if tgClient is None:
                self.log.info(
                    f"<red>└─ ❌ Account {self.accountName} session is not connected!</red>"
                )
                return None
            else:
                self.log.info(
                    f"<green>└─ 🔑 {self.accountName} session is loaded successfully!</green>"
                )
            await self.accountSetup()

            return True
        except Exception as e:
            self.log.info(
                f"<yellow>└─ ❌ {self.accountName} session failed to authorize!</yellow>"
            )
            self.log.error(f"<red>└─ ❌ {e}</red>")
            return False

    async def getWebViewData(self):
        referral = self.ReferralToken
        BotID = self.BotID

        tgClient = await self.Connect()
        if tgClient is None:
            self.log.info(
                f"<yellow>└─ ❌ Account {self.accountName} session is not connected!</yellow>"
            )
            return None

        bot_started = False
        try:
            chatHistory = await self.tgClient.get_chat_history_count(BotID)
            if chatHistory > 0:
                bot_started = True
        except Exception as e:
            pass

        try:
            if not bot_started:
                peer = await self.tgClient.resolve_peer(BotID)
                await self.tgClient.invoke(
                    functions.messages.StartBot(
                        bot=peer,
                        peer=peer,
                        random_id=random.randint(100000, 999999),
                        start_param=referral,
                    )
                )

            peer = await tgClient.resolve_peer(BotID)
            bot_app = None
            if self.ShortAppName:
                bot_app = InputBotAppShortName(
                    bot_id=peer, short_name=self.ShortAppName
                )
            web_view = None

            if bot_app:
                web_view = await tgClient.invoke(
                    RequestAppWebView(
                        peer=peer,
                        app=bot_app,
                        platform="android",
                        write_allowed=True,
                        start_param=referral,
                    )
                )
            else:
                web_view = await tgClient.invoke(
                    RequestWebView(
                        peer=peer,
                        bot=peer,
                        platform="android",
                        from_bot_menu=False,
                        url=self.AppURL,
                    )
                )

            auth_url = web_view.url
            web_data = unquote(
                string=auth_url.split("tgWebAppData=", maxsplit=1)[1].split(
                    "&tgWebAppVersion", maxsplit=1
                )[0]
            )

            self.log.info(
                f"<green>└─ 🔑 {self.accountName} session is authorized!</green>"
            )

            return web_data
        except Exception as e:
            self.log.info(
                f"<yellow>└─ ❌ {self.accountName} session failed to authorize!</yellow>"
            )
            self.log.error(f"<red>└─ ❌ {e}</red>")
            return None

    async def accountSetup(self):
        tgClient = await self.Connect()
        if tgClient is None:
            self.log.info(
                f"<y>└─ ❌ Account {self.accountName} session is not connected!</y>"
            )
            return None

        try:
            await self.joinChat("MasterCryptoFarmBot", True, False)

            UserAccount = await tgClient.get_me()
            if not UserAccount.username:
                self.log.info(
                    f"<green>└─ 🗿 Account username is empty. Setting a username for the account...</green>"
                )
                setUsername = False
                maxTries = 5
                while not setUsername and maxTries > 0:
                    RandomUsername = "".join(
                        random.choices(string.ascii_lowercase, k=random.randint(15, 30))
                    )
                    self.log.info(
                        f"<green>└─ 🗿 Setting username for {self.accountName} session, New username <cyan>{RandomUsername}</cyan></green>"
                    )
                    setUsername = await tgClient.set_username(RandomUsername)
                    maxTries -= 1
                    await time.sleep(5)

            self.log.info(
                f"<green>└─ ✅ Account {self.accountName} session is setup successfully!</green>"
            )

        except Exception as e:
            self.log.info(
                f"<y>└─ ❌ Account {self.accountName} session is not setup!</y>"
            )
            self.log.error(f"<red>└─ ❌ {e}</red>")
            return None

    async def joinChat(self, url, noLog=False, mute=True):
        if not noLog:
            self.log.info(f"<green>└─ 📰 Joining <cyan>{url}</cyan> ...</green>")
        tgClient = await self.Connect()
        if tgClient is None:
            if noLog:
                return None
            self.log.info(
                f"<y>└─ ❌ Account {self.accountName} session is not connected!</y>"
            )
            return None

        try:
            chatObj = await tgClient.join_chat(url)

            if chatObj is None or not chatObj.id:
                return None

            if mute:
                peer = InputNotifyPeer(peer=await tgClient.resolve_peer(chatObj.id))
                settings = InputPeerNotifySettings(
                    silent=True, mute_until=int(time.time() + 10 * 365 * 24 * 60 * 60)
                )
                res = await tgClient.invoke(
                    UpdateNotifySettings(peer=peer, settings=settings)
                )

            if noLog:
                return None

            self.log.info(
                f"<green>└─ ✅ <cyan>{url}</cyan> has been joined successfully!</green>"
            )
            return True
        except Exception as e:
            if noLog:
                return None

            self.log.info(f"<y>└─ ❌ </y><cyan>{url}</cyan><y> failed to join!</y>")
            self.log.error(f"<red>❌ {e}</red>")
            return False

    async def setName(self, firstName, lastName=None):
        tgClient = await self.Connect()
        if tgClient is None:
            self.log.info(
                f"<y>└─ ❌ Account {self.accountName} session is not connected!</y>"
            )
            return None
        tgMe = await tgClient.get_me()
        firstName = tgMe.first_name if not firstName else firstName
        lastName = tgMe.last_name if not lastName else lastName
        try:
            await tgClient.update_profile(first_name=firstName, last_name=lastName)
            self.log.info(
                f"<green>└─ ✅ Account {self.accountName} session name is set successfully!</green>"
            )
            return True
        except Exception as e:
            self.log.info(
                f"<yellow>└─ ❌ Failed to set session {self.accountName} name!</yellow>"
            )
            self.log.error(f"<red>❌ {e}</red>")
            return False

    async def getMe(self):
        tgClient = await self.Connect()
        if tgClient is None:
            self.log.info(
                f"<yellow>└─ ❌ Account {self.accountName} session is not connected!</yellow>"
            )
            return None
        tgMe = await tgClient.get_me()
        return tgMe

    async def DisconnectClient(self):
        if self.tgClient is not None and self.tgClient.is_connected:
            self.log.info(f"<g>└─ 💻 Disconnecting {self.accountName} session ...</g>")
            await self.tgClient.disconnect()
            self.log.info(
                f"<green>└─── ❌ {self.accountName} session has been disconnected successfully!</green>"
            )
        return True
