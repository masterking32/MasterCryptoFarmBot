FROM python:3.13.0-slim

LABEL version="1.1"
LABEL description="MasterCryptoFarmBot Docker Image"

RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN echo '#!/bin/bash\n\
set -e\n\
\n\
if ! git config --get-regexp init.defaultBranch | grep -q main; then\n\
    git config --global init.defaultBranch main\n\
fi\n\
\n\
if [ ! -f main.py ]; then\n\
    echo "Cloning repository..."\n\
    git clone https://github.com/masterking32/MasterCryptoFarmBot.git ./\n\
fi\n\
\n\
if ! git config --get-regexp safe.directory | grep -q /MasterCryptoFarmBot; then\n\
    git config --global --add safe.directory /MasterCryptoFarmBot\n\
fi\n\
\n\
if [ ! -f config.py ]; then\n\
    echo "Copying config from sample..."\n\
    cp config.py.sample config.py\n\
fi\n\
\n\
if [ -f start_linux.sh ]; then\n\
    echo "Launching..."\n\
    bash start_linux.sh\n\
else\n\
    echo "start_linux.sh not found, exiting."\n\
    exit 1\n\
fi' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

RUN useradd -m mcfuser && \
    mkdir -p /MasterCryptoFarmBot && \
    chown -R mcfuser:mcfuser /MasterCryptoFarmBot

USER mcfuser

RUN pip3 install --upgrade pip && \
    pip cache purge

WORKDIR /MasterCryptoFarmBot

ENTRYPOINT ["/entrypoint.sh"]
