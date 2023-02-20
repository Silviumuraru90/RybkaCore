FROM ubuntu:bionic

ENV DEBIAN_FRONTEND noninteractive

RUN     apt-get update && \
        apt-get -y upgrade && \
        apt-get install -y sudo
    
RUN     sudo apt-get install -y apt-utils git jq curl

RUN     apt-get install python3.8 -y && \
        apt-get install python3.8-dev -y && \
        apt install python3-pip -y

RUN     sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1 && \
        python3 -V

RUN     pip3 install multidict anybadge
RUN     pip3 install attrs yarl
RUN     pip3 install async_timeout charset_normalizer aiosignal cython
RUN     pip3 install websocket-client numpy click colored requests GPUtil psutil telepot termcolor
RUN     pip3 install python-binance python-telegram-bot

RUN	sudo apt install build-essential wget -y && \
        wget https://artiya4u.keybase.pub/TA-lib/ta-lib-0.4.0-src.tar.gz && \
        tar -xvf ta-lib-0.4.0-src.tar.gz && \
        cd ta-lib/ && \
        ls -alH && \
        chmod +x configure && \
        ./configure --build=x86_64-unknown-linux-gnu && \
        make && \
        sudo make install

RUN     pip3 install TA-Lib

RUN     pip3 freeze && \
        python3.8 -V && \
        pip3 --version && \
        bash --version

RUN     useradd -ms /bin/bash silviu && \
        usermod -aG sudo silviu && \
        echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers


USER silviu
WORKDIR /home/silviu

ENV DEBIAN_FRONTEND teletype

CMD ["/bin/bash"]
