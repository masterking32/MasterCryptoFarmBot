# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot
from urllib.parse import urlparse
import requests


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
    return parts[0] + ".***" + "." + parts[2] + "." + parts[3]
