#!/bin/bash

if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
elif type lsb_release &> /dev/null; then
    OS=$(lsb_release -si | tr '[:upper:]' '[:lower:]')
elif [ "$(uname -o)" == "Android" ]; then
    OS="android"
elif [ "$(uname)" == "Darwin" ]; then
    OS="darwin"
elif [ -f /etc/debian_version ]; then
    OS="debian"
elif [ -f /etc/fedora-release ]; then
    OS="fedora"
elif [ -f /etc/centos-release ]; then
    OS="centos"
else
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
fi

PACKAGE_MANAGER=""
if [ "$OS" == "ubuntu" ] || [ "$OS" == "debian" ]; then
    PACKAGE_MANAGER="apt"
elif [ "$OS" == "fedora" ] || [ "$OS" == "centos" ]; then
    PACKAGE_MANAGER="yum"
elif [ "$OS" == "darwin" ]; then
    PACKAGE_MANAGER="brew"
elif [ "$OS" == "android" ]; then
    PACKAGE_MANAGER="pkg"
fi

PACKAGE_MANAGER_UPDATE=""
if [ "$PACKAGE_MANAGER" == "apt" ]; then
    PACKAGE_MANAGER_UPDATE="sudo apt update"
elif [ "$PACKAGE_MANAGER" == "yum" ]; then
    PACKAGE_MANAGER_UPDATE="sudo yum update"
elif [ "$PACKAGE_MANAGER" == "brew" ]; then
    PACKAGE_MANAGER_UPDATE="brew update"
elif [ "$PACKAGE_MANAGER" == "pkg" ]; then
    PACKAGE_MANAGER_UPDATE="pkg update"
fi

PACKAGE_MANAGER_UPGRADE=""
if [ "$PACKAGE_MANAGER" == "apt" ]; then
    PACKAGE_MANAGER_UPGRADE="sudo apt upgrade -y"
elif [ "$PACKAGE_MANAGER" == "yum" ]; then
    PACKAGE_MANAGER_UPGRADE="sudo yum upgrade -y"
elif [ "$PACKAGE_MANAGER" == "brew" ]; then
    PACKAGE_MANAGER_UPGRADE="brew upgrade"
elif [ "$PACKAGE_MANAGER" == "pkg" ]; then
    PACKAGE_MANAGER_UPGRADE="pkg upgrade -y"
fi

PACKAGE_MANAGER_INSTALL=""
if [ "$PACKAGE_MANAGER" == "apt" ]; then
    PACKAGE_MANAGER_INSTALL="sudo apt install -y"
elif [ "$PACKAGE_MANAGER" == "yum" ]; then
    PACKAGE_MANAGER_INSTALL="sudo yum install -y"
elif [ "$PACKAGE_MANAGER" == "brew" ]; then
    PACKAGE_MANAGER_INSTALL="brew install"
elif [ "$PACKAGE_MANAGER" == "pkg" ]; then
    PACKAGE_MANAGER_INSTALL="pkg install -y"
fi

if ! command -v git &> /dev/null; then
    echo "Git is not installed. Please install Git and try again."
    if [ $PACKAGE_MANAGER == "" ]; then
        exit 1
    fi

    echo "Do you want to install Git? (y/n)"
    read -r INSTALL_GIT
    if [ "$INSTALL_GIT" == "y" ]; then
        $PACKAGE_MANAGER_UPDATE
        $PACKAGE_MANAGER_UPGRADE
        $PACKAGE_MANAGER_INSTALL git
    else
        exit 1
    fi
fi

PIP=""
PYTHON=""

if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "Python is not installed. Please install Python and try again."
    if [ $PACKAGE_MANAGER == "" ]; then
        exit 1
    fi
    echo "Do you want to install Python? (y/n)"
    read -r INSTALL_PYTHON
    if [ "$INSTALL_PYTHON" == "y" ]; then
        $PACKAGE_MANAGER_UPDATE
        $PACKAGE_MANAGER_UPGRADE
        $PACKAGE_MANAGER_INSTALL python3
        PYTHON=python3
    else
        exit 1
    fi
fi

if command -v pip3 &> /dev/null; then
    PIP=pip3
elif command -v pip &> /dev/null; then
    PIP=pip
else
    echo "Pip is not installed. Please install Pip and try again."
    if [ $PACKAGE_MANAGER == "" ]; then
        exit 1
    fi
    echo "Do you want to install Pip? (y/n)"
    read -r INSTALL_PIP
    if [ "$INSTALL_PIP" == "y" ]; then
        $PACKAGE_MANAGER_UPDATE
        $PACKAGE_MANAGER_UPGRADE
        $PACKAGE_MANAGER_INSTALL python3-pip
        if [ "$OS" == "arch" ]; then
            $PACKAGE_MANAGER_INSTALL python-pip
        fi
        PIP=pip3
    else
        exit 1
    fi
fi

echo "=========================================="
echo "Press CTRL+C to stop the bot"
echo "=========================================="
sleep 3

while true; do
    # update the bot
    echo "=========================================="
    echo "Updating bot..."
    echo "=========================================="
    git config pull.rebase false
    git stash
    echo "Stashed changes"
    git pull origin main
    git stash pop
    echo "Popped changes"
    if [ $? -ne 0 ]; then
        echo "Failed to update the bot. Retrying in 5 seconds..."
        sleep 5
        continue
    fi
    echo "Project updated successfully"
    sleep 2

    echo "=========================================="
    echo "Updating dependencies..."
    echo "=========================================="
    # if pip3 dont use --break-system-packages
    if [ "$PIP" == "pip3" ]; then
        $PIP install -U -r requirements.txt
    else
        $PIP install -U --break-system-packages -r requirements.txt
    fi
    if [ $? -ne 0 ]; then
        echo "Failed to update dependencies. Retrying in 5 seconds..."
        sleep 5
        continue
    fi
    echo "Dependencies updated successfully"
    sleep 2

    echo "=========================================="
    echo "Starting bot..."
    echo "=========================================="
    $PYTHON main.py
    if [ $? -ne 0 ]; then
        echo "Bot encountered an error. Restarting in 5 seconds..."
    else
        echo "Bot stopped. Restarting in 5 seconds..."
    fi
    sleep 5
done

trap 'echo "=========================================="; echo "CTRL+C pressed. Exiting..."; exit 0' SIGINT
