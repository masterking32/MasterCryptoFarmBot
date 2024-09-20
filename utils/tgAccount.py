# Developed by: MasterkinG32
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
import utils.logColors as lc


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
            self.log.error(f"{lc.r}└─ ❌ Proxy {self.proxy} is not working!{lc.rs}")
            return None

        self.tgClient = Client(
            name=self.accountName,
            api_id=self.bot_globals["telegram_api_id"],
            api_hash=self.bot_globals["telegram_api_hash"],
            workdir=self.bot_globals["mcf_dir"] + "/telegram_accounts",
            plugins=dict(root="bot/plugins"),
            proxy=parseProxy(self.proxy) if self.proxy else None,
        )

        self.log.info(f"{lc.g}└─ 🌍 Connecting {self.accountName} session ...{lc.rs}")
        try:
            isConnected = await self.tgClient.connect()
            if isConnected:
                self.log.info(
                    f"{lc.g}└─ 🌍 Session {self.accountName} connected successfully!{lc.rs}"
                )
                return self.tgClient
            else:
                return None
        except Exception as e:
            self.log.error(f"└─ ❌ {e}")
            return None

    async def run(self):
        try:
            self.log.info(f"{lc.g}🤖 Running {self.accountName} account ...{lc.rs}")
            if not os.path.exists(
                self.bot_globals["mcf_dir"]
                + f"/telegram_accounts/{self.accountName}.session"
            ):
                self.log.error(
                    f"{lc.r}❌ Account {self.accountName} session is not found!{lc.rs}"
                )
                return None

            self.log.info(f"{lc.g}└─ 🔑 Loading {self.accountName} session ...{lc.rs}")

            tgClient = await self.Connect()
            if tgClient is None:
                self.log.error(
                    f"{lc.r}└─ ❌ Account {self.accountName} session is not connected!{lc.rs}"
                )
                return None
            else:
                self.log.info(
                    f"{lc.g}└─ 🔑 {self.accountName} session is loaded successfully!{lc.rs}"
                )
            await self.accountSetup()

            return True
        except Exception as e:
            self.log.error(
                f"{lc.r}└─ ❌ {self.accountName} session failed to authorize!{lc.rs}"
            )
            self.log.error(f"{lc.r}└─ ❌ {e}{lc.rs}")
            return False

    async def getWebViewData(self):
        referral = self.ReferralToken
        BotID = self.BotID

        tgClient = await self.Connect()
        if tgClient is None:
            self.log.error(
                f"{lc.r}└─ ❌ Account {self.accountName} session is not connected!{lc.rs}"
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
                f"{lc.g}└─ 🔑 {self.accountName} session is authorized!{lc.rs}"
            )

            return web_data
        except Exception as e:
            self.log.error(
                f"{lc.r}└─ ❌ {self.accountName} session failed to authorize!{lc.rs}"
            )
            self.log.error(f"{lc.r}└─ ❌ {e}{lc.rs}")
            return None

    async def accountSetup(self):
        tgClient = await self.Connect()
        if tgClient is None:
            self.log.error(
                f"{lc.r}└─ ❌ Account {self.accountName} session is not connected!{lc.rs}"
            )
            return None

        try:
            await self.joinChat("MasterCryptoFarmBot", True, False)

            UserAccount = await tgClient.get_me()
            if not UserAccount.username:
                self.log.info(
                    f"{lc.g}└─ 🗿 Account username is empty. Setting a username for the account...{lc.rs}"
                )
                setUsername = False
                maxTries = 5
                while not setUsername and maxTries > 0:
                    RandomUsername = "".join(
                        random.choices(string.ascii_lowercase, k=random.randint(15, 30))
                    )
                    self.log.info(
                        f"{lc.g}└─ 🗿 Setting username for {self.accountName} session, New username {lc.rs + lc.c + RandomUsername + lc.rs}"
                    )
                    setUsername = await tgClient.set_username(RandomUsername)
                    maxTries -= 1
                    await time.sleep(5)

            self.log.info(
                f"{lc.g}└─ ✅ Account {self.accountName} session is setup successfully!{lc.rs}"
            )

        except Exception as e:
            self.log.error(
                f"{lc.r}└─ ❌ Account {self.accountName} session is not setup!{lc.rs}"
            )
            self.log.error(f"{lc.r}└─ ❌ {e}{lc.rs}")
            return None

    async def joinChat(self, url, noLog=False, mute=True):
        if not noLog:
            self.log.info(
                f"{lc.g}└─ 📰 Joining {lc.rs + lc.c + url + lc.rs + lc.g} ...{lc.rs}"
            )
        tgClient = await self.Connect()
        if tgClient is None:
            if noLog:
                return None
            self.log.error(
                f"{lc.r}└─ ❌ Account {self.accountName} session is not connected!{lc.rs}"
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
                f"{lc.g}└─ ✅ {lc.rs + lc.c + url + lc.rs + lc.g} has been joined successfully!{lc.rs}"
            )
            return True
        except Exception as e:
            if noLog:
                return None

            self.log.error(
                f"{lc.r}└─ ❌ {lc.rs + lc.c + url + lc.rs + lc.r} failed to join!{lc.rs}"
            )
            self.log.error(f"{lc.r}❌ {e}{lc.rs}")
            return False

    async def setName(self, firstName, lastName=None):
        tgClient = await self.Connect()
        if tgClient is None:
            self.log.error(
                f"{lc.r}└─ ❌ Account {self.accountName} session is not connected!{lc.rs}"
            )
            return None
        tgMe = await tgClient.get_me()
        firstName = tgMe.first_name if not firstName else firstName
        lastName = tgMe.last_name if not lastName else lastName
        try:
            await tgClient.update_profile(first_name=firstName, last_name=lastName)
            self.log.info(
                f"{lc.g}└─ ✅ Account {self.accountName} session name is set successfully!{lc.rs}"
            )
            return True
        except Exception as e:
            self.log.error(
                f"{lc.r}└─ ❌ Failed to set session {self.accountName} name!{lc.rs}"
            )
            self.log.error(f"{lc.r}❌ {e}{lc.rs}")
            return False

    async def getMe(self):
        tgClient = await self.Connect()
        if tgClient is None:
            self.log.error(
                f"{lc.r}└─ ❌ Account {self.accountName} session is not connected!{lc.rs}"
            )
            return None
        tgMe = await tgClient.get_me()
        return tgMe

    async def DisconnectClient(self):
        if self.tgClient is not None and self.tgClient.is_connected:
            self.log.info(f"└─ 💻 Disconnecting {self.accountName} session ...")
            await self.tgClient.disconnect()
            self.log.info(
                f"{lc.g}└─── ❌ {self.accountName} session has been disconnected successfully!{lc.rs}"
            )
        return True
