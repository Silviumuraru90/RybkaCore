FROM ubuntu:bionic

ENV DEBIAN_FRONTEND noninteractive

RUN     apt-get update && \
        apt-get -y upgrade && \
        apt-get install -y \
        sudo
    
RUN     sudo apt-get install -y apt-utils

RUN     sudo apt-get install -y git

RUN     apt-get install python3.8 -y
RUN     sudo apt-get install python3.8-dev -y
RUN     apt install python3-pip -y

RUN     sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1

RUN     python3 -V

RUN     pip3 install multidict
RUN     pip3 install attrs
RUN     pip3 install yarl
RUN     pip3 install async_timeout
RUN     pip3 install charset_normalizer
RUN     pip3 install aiosignal
RUN     pip3 install cython
RUN     pip3 install websocket-client
RUN     pip3 install python-binance
RUN     pip3 install numpy

RUN	sudo apt install build-essential wget -y
RUN	wget https://artiya4u.keybase.pub/TA-lib/ta-lib-0.4.0-src.tar.gz
RUN	tar -xvf ta-lib-0.4.0-src.tar.gz
RUN	cd ta-lib/ && \
        ls -alH && \
        chmod +x configure && \
        ./configure --build=x86_64-unknown-linux-gnu && \
        make && \
        sudo make install

RUN     pip3 install TA-Lib

RUN     pip3 freeze

RUN     python3.8 -V
RUN     pip3 --version
RUN     bash --version

RUN     useradd -ms /bin/bash silviu && \
        usermod -aG sudo silviu

RUN     echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers


USER silviu
WORKDIR /home/silviu

ENV DEBIAN_FRONTEND teletype

CMD ["/bin/bash"]
