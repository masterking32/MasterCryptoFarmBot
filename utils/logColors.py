# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot
import logging
from colorlog import ColoredFormatter
from logging.handlers import RotatingFileHandler


def getLogger(logFile=None, max_log_size=1024 * 1024 * 1, backup_count=3):
    # ---------------------------------------------#
    # Logging configuration
    LOG_LEVEL = logging.DEBUG
    # Include date and time in the log format
    LOGFORMAT = f"{cb}[MasterCryptoFarmBot]{rs} {bt}[%(asctime)s]{bt} %(log_color)s[%(levelname)s]%(reset)s %(log_color)s%(message)s%(reset)s"

    logging.root.setLevel(LOG_LEVEL)
    formatter = ColoredFormatter(
        LOGFORMAT, "%Y-%m-%d %H:%M:%S"
    )  # Specify the date/time format

    LOGFILE_FORMAT = "[MasterCryptoFarmBot] [%(asctime)s] [%(levelname)s] %(message)s"
    file_formatter = logging.Formatter(LOGFILE_FORMAT, "%Y-%m-%d %H:%M:%S")

    stream = logging.StreamHandler()
    stream.setLevel(LOG_LEVEL)
    stream.setFormatter(formatter)
    log = logging.getLogger("pythonConfig")
    log.setLevel(LOG_LEVEL)
    log.addHandler(stream)
    if logFile:
        file_handler = RotatingFileHandler(
            logFile, maxBytes=max_log_size, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setFormatter(file_formatter)
        log.addHandler(file_handler)

    # End of configuration
    # ---------------------------------------------#
    return log


# # Regular Text Colors
bl = "\033[30m"  # black
r = "\033[31m"  # red
g = "\033[32m"  # green
y = "\033[33m"  # yellow
b = "\033[34m"  # blue
m = "\033[35m"  # magenta
c = "\033[36m"  # cyan
w = "\033[37m"  # white

# Bright Text Colors
blt = "\033[90m"  # black_bright
rt = "\033[91m"  # red_bright
gt = "\033[92m"  # green_bright
yt = "\033[93m"  # yellow_bright
bt = "\033[94m"  # blue_bright
mt = "\033[95m"  # magenta_bright
ct = "\033[96m"  # cyan_bright
wt = "\033[97m"  # white_bright

# Bold Text Colors
blb = "\033[1;30m"  # black_bold
rb = "\033[1;31m"  # red_bold
gb = "\033[1;32m"  # green_bold
yb = "\033[1;33m"  # yellow_bold
bb = "\033[1;34m"  # blue_bold
mb = "\033[1;35m"  # magenta_bold
cb = "\033[1;36m"  # cyan_bold
wb = "\033[1;37m"  # white_bold

# Reset Color
rs = "\033[0m"
