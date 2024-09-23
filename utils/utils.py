# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

from datetime import datetime
from urllib.parse import urlparse
import requests
import re


def parseProxy(proxy_url):
    if not proxy_url:
        return None
    parsed = urlparse(proxy_url)
    proxy_dict = {
        "scheme": parsed.scheme,
        "hostname": parsed.hostname,
        "port": parsed.port,
        "username": parsed.username,
        "password": parsed.password,
    }
    return proxy_dict


def getConfig(config, key, default=None):
    if key in config:
        return config[key]
    return default


def testProxy(proxy_url):
    if not proxy_url:
        return True
    proxy_dict = {
        "http": proxy_url,
        "https": proxy_url,
    }
    try:
        resp = requests.get(
            "https://api.masterking32.com/ip.php", proxies=proxy_dict, timeout=15
        )
        if resp.status_code == 200:
            return True
        return False
    except Exception as e:
        return False


def HideIP(ip):
    if not ip:
        return None

    if ":" in ip:
        return ip[:6] + "****" + ip[-6:]
    parts = ip.split(".")
    return parts[0] + "." + parts[1] + ".***.***"


def RemoveConsoleColor(text):
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def ansi_to_html(text):
    text = text.replace("\x1b[0m", "</span>")
    text = text.replace("\x1b[1m", '<span style="font-weight: bold;">')
    text = text.replace("\x1b[3m", '<span style="font-style: italic;">')
    text = text.replace("\x1b[4m", '<span style="text-decoration: underline;">')
    text = text.replace("\x1b[31m", '<span style="color: red;">')
    text = text.replace("\x1b[32m", '<span style="color: green;">')
    text = text.replace("\x1b[33m", '<span style="color: yellow;">')
    text = text.replace("\x1b[34m", '<span style="color: blue;">')
    text = text.replace("\x1b[35m", '<span style="color: magenta;">')
    text = text.replace("\x1b[36m", '<span style="color: cyan;">')
    text = text.replace("\x1b[37m", '<span style="color: white;">')
    text = text.replace("\n", "<br>")
    text = text.replace("\r", "")
    return text + "</span>"


def TimeAgo(time):
    if not time:
        return "Unknown"

    if isinstance(time, str):
        time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")

    now = datetime.now()
    diff = (now - time).total_seconds()

    if diff < 60:
        return f"{int(diff)} seconds"
    if diff < 3600:
        return f"{int(diff // 60)} minutes"
    if diff < 86400:
        return f"{int(diff // 3600)} hours"
    return f"{int(diff // 86400)} days"
