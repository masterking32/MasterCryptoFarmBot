#!/bin/bash

# check if git exists
if ! command -v git &> /dev/null; then
    echo "Git is not installed. Please install Git and try again."
    exit 1
fi

# check if pip exists
if ! command -v pip &> /dev/null; then
    echo "Pip is not installed. Please install python3-pip and try again."
    exit 1
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
    git pull origin main
    if [ $? -ne 0 ]; then
        echo "Failed to update the bot. Retrying in 5 seconds..."
        sleep 5
        continue
    fi
    echo "Project updated successfully"
    sleep 2

    # updating requirements
    echo "=========================================="
    echo "Updating requirements..."
    echo "=========================================="
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt > /dev/null 2>&1
        if [ $? -ne 0 ]; then
            echo "Failed to install required libraries. Exiting..."
            exit 1
        else
            echo "Update requirements successfully."
        fi
    else
        echo "requirements.txt not found. Skipping library check..."
    fi
    sleep 2

    # start the bot
    echo "=========================================="
    echo "Starting bot..."
    echo "=========================================="
    python3 main.py
    if [ $? -ne 0 ]; then
        echo "Bot encountered an error. Restarting in 5 seconds..."
    else
        echo "Bot stopped. Restarting in 5 seconds..."
    fi
    sleep 5
done

trap 'echo "=========================================="; echo "CTRL+C pressed. Exiting..."; exit 0' SIGINT
