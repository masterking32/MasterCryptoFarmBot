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
    ansi_to_html_map = {
        "\x1b[0m": "</span>",
        "\x1b[1m": '<span style="font-weight: bold;">',
        "\x1b[3m": '<span style="font-style: italic;">',
        "\x1b[4m": '<span style="text-decoration: underline;">',
        "\x1b[31m": '<span style="color: red;">',
        "\x1b[32m": '<span style="color: green;">',
        "\x1b[33m": '<span style="color: yellow;">',
        "\x1b[34m": '<span style="color: blue;">',
        "\x1b[35m": '<span style="color: magenta;">',
        "\x1b[36m": '<span style="color: cyan;">',
        "\x1b[37m": '<span style="color: white;">',
        "\n": "<br>",
        "\r": "",
        "<red>": '<span style="color: red;">',
        "<green>": '<span style="color: green;">',
        "<yellow>": '<span style="color: yellow;">',
        "<blue>": '<span style="color: blue;">',
        "<magenta>": '<span style="color: magenta;">',
        "<cyan>": '<span style="color: cyan;">',
        "<white>": '<span style="color: white;">',
        "</red>": "</span>",
        "</green>": "</span>",
        "</yellow>": "</span>",
        "</blue>": "</span>",
        "</magenta>": "</span>",
        "</cyan>": "</span>",
        "</white>": "</span>",
        "<r>": '<span style="color: red;">',
        "<g>": '<span style="color: green;">',
        "<y>": '<span style="color: yellow;">',
        "<b>": '<span style="color: blue;">',
        "<m>": '<span style="color: magenta;">',
        "<c>": '<span style="color: cyan;">',
        "<w>": '<span style="color: white;">',
        "</r>": "</span>",
        "</g>": "</span>",
        "</y>": "</span>",
        "</b>": "</span>",
        "</m>": "</span>",
        "</c>": "</span>",
        "</w>": "</span>",
    }

    for ansi_code, html_code in ansi_to_html_map.items():
        text = text.replace(ansi_code, html_code)

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
