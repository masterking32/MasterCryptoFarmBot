FROM debian:stable-slim

LABEL version="1.3"
LABEL description="MasterCryptoFarmBot Docker Image"

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libsqlite3-dev \
    libreadline-dev \
    libffi-dev \
    curl \
    libbz2-dev \
    git \
    ca-certificates \
    sqlite3 \
    libsqlite3-dev

RUN wget https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz \
    && tar -xf Python-3.12.0.tgz \
    && cd Python-3.12.0 \
    && ./configure --enable-optimizations --with-ensurepip=install \
    && make -j $(nproc) \
    && make altinstall \
    && cd .. \
    && rm -rf Python-3.12.0 Python-3.12.0.tgz

RUN update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.12 1 \
    && update-alternatives --set python3 /usr/local/bin/python3.12 \
    && update-alternatives --install /usr/bin/pip3 pip3 /usr/local/bin/pip3.12 1 \
    && update-alternatives --set pip3 /usr/local/bin/pip3.12

RUN apt-get purge -y \
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libsqlite3-dev \
    libreadline-dev \
    libffi-dev \
    libbz2-dev \
    wget \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

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

RUN pip3 install --user --upgrade pip && \
    pip3 cache purge

WORKDIR /MasterCryptoFarmBot

ENTRYPOINT ["/entrypoint.sh"]
