# 💱 Rybka

<br>

## &emsp;&emsp; **Description**
<br>
📌 `Rybka` bot is a scalping crypto-trading-bot that currently supports the following pair(s):<br><br>
&emsp;&emsp;✅ EGLDUSDT <br>
&emsp;&emsp;⛏ &nbsp;`more in the future` <br><br><br>

📌 It uses 🔌 socket connection to Binance via the `python-binance` lib <br><br>

📌 It is a cross-OS software that has been tested on: <br><br>
&emsp;&emsp;✅ Ubuntu 18.04 (`bionic`) <br>
&emsp;&emsp;❔ &nbsp;Ubuntu 20.04 <br>
&emsp;&emsp;❔ &nbsp;Ubuntu 22.04 <br>
&emsp;&emsp;✅ Debian 10 (`buster`) <br>
&emsp;&emsp;✅ Win 10 <br>
&emsp;&emsp;❔ &nbsp;Mac OS <br><br>


> **Legend:** &emsp; ❔ &nbsp; ⟹ &nbsp; _not tested yet_


<br><br>

***

## &emsp;&emsp; **Features supported**
<br>

> ✅ Automated technical analysis (scalping mode) (based on a relative strength index - RSI) <br>
✅ Automatic `rybka.py` bot `restarter.py` add-on in case of network failures, local software failures <br>
✅ Supports a `LIVE` MODE with connection to the actual Binance wallet of the user, as well as a `DEMO` MODE of the product, with fake data of a virtualized wallet <br>
✅ Creates separate local logs, considering the MODE the bot is in and tracks those independent of each other across multiple runs <br>
✅ File exports for a variety of useful information, logs or configuration data needed for the time it might restart via `restarter.py` - so to always grab back the work from where it left it <br>
✅ Regular back-ups of imp. files <br>
✅ Individual buys tracking <br>
✅ Errors catch mechanism and exception management <br>
✅ Uptime tracking <br>
✅ Email notif. module. Informs the user about being low on BNB, or on USDT, or if an error occured and bot got shutdown. Also sends emails on start / restart actions <br>
✅ Dynamic adjustment (greediness) for buy-sell math of the trading pair <br>
✅ Live wallet data displayed for the trade pair sides and commission, dynamic adjustment with each buy - sell <br>
✅ Folder creation (name including date and hour) with files containing important data of the current run and auto-archive system once the run is finished <br>
✅ Make bot sell multiple bought crypto-coins at once, if signal allows it (dynamically) <br>
✅ Upscale the trading quantity if user set it too low, so low that it hits the minimum 10💲 lower limit Binance imposed for a buy action <br>
✅ Clear profit tracked in time <br>
✅ Nr. of buy trades tracked in time <br>
✅ Colored log output based on log-level types (INFO, WARN, FATAL and DEBUG / VERBOSE / HIGH_VERBOSITY) <br>
✅ Timestamp added on bot's actions - logs, back-ups, trades, etc <br>
✅ Cross-OS support (Win / Linux-based) <br>
✅ Check which amount of the USDT is locked (in limit / stop orders, etc.) and avoids using it <br>
✅ Local files check on each start / restart action, even integrity check for files' values <br>

<br><br>

***

## &emsp;&emsp; **Prerequisites**
<br>
As `rybka` is not a standalone executable software yet, for any of the aforementioned OS listed, it manages to achieve cross-OS status directly via `python`. Currently compatible python versions: <br><br>
&emsp;&emsp;✅ Python 3.6 <br>
&emsp;&emsp;✅ Python 3.7 <br>
&emsp;&emsp;✅ Python 3.8 <br>
&emsp;&emsp;❔ &nbsp;Python 3.9 <br>
&emsp;&emsp;❔ &nbsp;Python 3.10 <br><br><br>

Hence, at the moment, you will need 🐍 `python` in your OS to run the software. Via pip, `4` modules would then come on top of your python installation: <br><br>
&emsp;&emsp;✅ python-binance <br>
&emsp;&emsp;✅ websocket-client <br>
&emsp;&emsp;✅ numpy <br>
&emsp;&emsp;✅ TA-Lib <br><br><br>

❗️ `Note:` while via `pip3` you are able to install the first three modules, the 4th (`TA-Lib`) is not within the official `pypi` list, hence you can download the `wheel` file that matches your `python` version and then install it via `pip`. <br> Grab the file from 📦 [HERE](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib) <br><br>
OR <br><br>
📦 Build it from source with these commands and then install it in the same way, via `pip`. Commands:
```
wget https://artiya4u.keybase.pub/TA-lib/ta-lib-0.4.0-src.tar.gz
tar -xvf ta-lib-0.4.0-src.tar.gz
cd ta-lib/ && \
ls -alH && \
chmod +x configure && \
./configure --build=x86_64-unknown-linux-gnu && \
make && \
sudo make install
```
<br>

❗️ `Note:` bot currently requires admin-level access on Windows in order to run, for it to be able to constantly synchronize the time with NIST's `time.nist.gov` server. This is NOT applicable for Linux-based distributions, where the de-sync issue has not been noticed

<br><br>

***

## &emsp;&emsp; **Getting started**
<br>

To run the software, beside the `prerequisites`, you will also need: <br><br>

🔘 Some `ENV` variables set: <br>

| VARIABLE                                 | TYPE   |   DESCRIPTION                                                                      | MANDATORY ? |  DEFAULT VALUE | 
|:-------------------------------------------|:------:|:------:|:----------------------------------------------------------------------------------:| :--------:|
|`RYBKA_DEBUG_LVL`                      | integer | Values ➡️ `1`, `2` or `3` <br>1️⃣ ➜ <b>Debug</b> &emsp; &emsp; &emsp;&nbsp;<br> 2️⃣ ➜ <b>Verbose</b> &emsp; &emsp; &nbsp;&nbsp; <br> 3️⃣ ➜ <b>&nbsp;High Verbosity</b><br> (Get from environment)                           | ❌        | ❌ | 
|`RYBKA_MODE `                           | string | Values ➡️ `DEMO` or `LIVE` <br> (Get from environment)                           | ❌        | `DEMO` | 
|`BIN_KEY`                              | string | Binance <b>Auth</b>orization <b>KEY</b> <br> (Get from environment)                            | ✅ <br> if `RYBKA_MODE` is either `LIVE` or `DEMO`        | ❌ | 
|`BIN_SECRET`                           | string | Binance <b>Auth</b>orization <b>SECRET</b> <br> (Get from environment)                           | ✅ <br> if `RYBKA_MODE` is either `LIVE` or `DEMO`      | ❌ | 
|`RYBKA_RSI_FOR_BUY`                     | integer | <b>RSI threshold for BUY</b> actions <br> Values ➡️ (`0` ↔️ `50`) <br> The higher the value, the more sensitive the bot on buy actions <br> (Get from environment)                           | ❌        | `30` | 
|`RYBKA_RSI_FOR_SELL`                    | integer | <b>RSI threshold for SELL</b> actions <br> Values ➡️ (`50` ↔️ `100`) <br> The lower the value, the more sensitive the bot on sell actions <br> (Get from environment)                           | ❌        | `70` | 
|`RYBKA_TRADE_QUANTITY`                  | integer | The <b>crypto-coin amount</b> to buy on each transaction <br> (Get from environment)                           | ❌        | `0.4` | 
|`RYBKA_MIN_PROFIT`                      | integer | The `USDT` <b>minimum profit</b>, per transaction, that allows a SELL signal to complete <br> (Get from environment)                           | ❌        | `0.25` | 
|`RYBKA_EMAIL_SWITCH`                    | boolean | Values ➡️ `True` or `False` <br> (Get from environment)                           | ❌        | `False` | 
|`RYBKA_EMAIL_SENDER_EMAIL`              | string | <b>Email</b> for the account sending the email <br> (Get from environment)                           | ✅ <br> if `RYBKA_EMAIL_SWITCH` is `True`       | ❌ | 
|`RYBKA_EMAIL_SENDER_DEVICE_PASSWORD`    | string | <b>DEVICE password</b>, not the emailbox password, (tested only with @gmail.com accounts) of the account sending the email  <br> (Get from environment)                           | ✅ <br> if `RYBKA_EMAIL_SWITCH` is `True`       | ❌ | 
|`RYBKA_EMAIL_RECIPIENT_EMAIL`           | string | <b>Email</b> for the account receiving the email <br> (Get from environment)                           | ✅ <br> if `RYBKA_EMAIL_SWITCH` is `True`        | ❌ | 
|`RYBKA_EMAIL_RECIPIENT_NAME`            | string | <b>Name</b> of the person receiving the email <br> (Get from environment)                           | ❌        | `User` | 
|`RYBKA_DISCLAIMER`                      | boolean | Values ➡️ `True` or `False` <br> (Get from environment)                           | ❌        | `True` | 
|`RYBKA_DEMO_BALANCE_USDT`                      | integer | Amount of `USDT` the bot is provided with, in `DEMO` mode <br> (Get from environment)                           | ❌        | `1500` | 
|`RYBKA_DEMO_BALANCE_EGLD`                      | integer | Amount of `EGLD` the bot is provided with, in `DEMO` mode <br> (Get from environment)                           | ❌        | `100` | 
|`RYBKA_DEMO_BALANCE_BNB`                      | integer | Amount of `BNB` the bot is provided with, in `DEMO` mode <br> (Get from environment)                           | ❌        | `0.2` | 

<br>

🔘 Some `USDT` for buy actions in your Binance wallet <br><br>

🔘 Some `BNB` amount in your Binance wallet (this is the currency used for trades' commission; `~100 trades = 1$ commission`) <br><br>

🔘 And, of course, an `internet connection` <br><br><br>

▶️ You can run the software directly (the `rybka.py` file) or via the `restarer.py` module that will automatically start the bot, but also restart the bot if it exits on a not-hardcoded error (such as a temporary internet drop) <br><br>

❗️ `Note:` Recommendation for having the best UI output - running `rybka` into a `cmd` shell within `Visual Studio Code` <br>


<br><br>

***
***

# <center> **More to know** </center> 


## 🟣 ![](https://img.shields.io/badge/Author%20and%20Acknowledgement-Questions-brightgreen)
<br>

| 👨‍💼 `Silviu-Iulian Muraru` | Contact Data |
|:---------------------------------------:|:---------------|
||![](https://img.shields.io/badge/silviumuraru90-%40yahoo.com-blue)
||[![](https://img.shields.io/badge/Linked-In-blue)](https://www.linkedin.com/in/silviu-muraru-iulian/)


<br>

***
## 🟣 [![](https://img.shields.io/gitlab/license/Silviu_space/rybka)](https://gitlab.com/Silviu_space/rybka/-/blob/master/LICENSE)

<br>

***
## 🟣 [![](https://img.shields.io/badge/project%20status-BETA-orange)](https://gitlab.com/Silviu_space/rybka/-/boards)

| Release lifecycle phases | Current lifecycle phase | Estimated date(s) of `start` / `finish` |
|:--------------------------------|:---------------:|:-----------------------:|
&emsp;&emsp; ✔️ `ALPHA`              |                 | August 2022 (`finished`)
&emsp;&emsp; 💻 `BETA` / `BETA TESTING`              |        ✅       | September 2022 (`started`)
&emsp;&emsp; 💻 `RELEASE CANDIDATE`  |                 | ⬛️
&emsp;&emsp; 💻 `GA`                 |                 | ⬛️

<br>

***
## 🟣 [![](https://img.shields.io/badge/-ROADMAP-green)](https://gitlab.com/Silviu_space/rybka/-/boards)
<br>

<b>🔜 There are still some pieces to move and cards to play:</b> <br>

>&emsp;&emsp; ♟ &nbsp;Get some inputs from a `config` file, not ENV. This way, users can edit some vars `on the fly`, while bot is still running and this to see them <br>
&emsp;&emsp; ♖ &nbsp;CLI args, at least for `RYBKA_MODE` values <br>
&emsp;&emsp; ♦︎ &nbsp;Switch to `binance-unicorn` instead of `python-binance`, in order to optime more the uptime <br>
&emsp;&emsp; ♞ &nbsp;Making the bot a `binary` file with all python modules packaged in <br>
&emsp;&emsp; ♡ &nbsp;&nbsp;Additional `reports` <br>
&emsp;&emsp; ♛ &nbsp;`Price alerts`, via inputs <br>
&emsp;&emsp; ♣︎ &nbsp;&nbsp;UI, perhaps through `Tkinter` lib <br>
&emsp;&emsp; ♥︎ &nbsp;`Safety net` implementation for USDT <br>
&emsp;&emsp; ♔ &nbsp;More `trade pairs` supported <br>
&emsp;&emsp; ♙ &nbsp;`Graps` provided as output <br>
&emsp;&emsp; ♘ &nbsp;`Profit tracking` over specfic periods of time, for better assesing the better / worse periods and adjust weights <br>
&emsp;&emsp; ♧ &nbsp;Addition `RSI` periods and `candlestick` periods, not only for scalping <br>
&emsp;&emsp; ♜ &nbsp;`Telegram` BOT (active mode) - providing `/commands` so thta users will be able to ask for information on the spot <br>
&emsp;&emsp; ♝ &nbsp;`Telegram` BOT (passive mode) - logging events in chat <br>
&emsp;&emsp; ♤&nbsp;`Orders` on demand <br>
&emsp;&emsp; ♠︎ &nbsp;&nbsp;&nbsp;Control the resulted `output files`' size <br>
&emsp;&emsp; ♕ &nbsp;`Always buy` policy <br>
&emsp;&emsp; ♚ &nbsp;`Always leave something to sell` at a higher profit <br>
&emsp;&emsp; ♗ &nbsp;`Code style` checks and `unit testing` + `coverage`, for a better integrity and stability / quicker testing <br>
&emsp;&emsp; ♢ &nbsp;Speed up internal processes by moving towards an `OOP` infrastructure / optimization <br>


<br>

And, of course, `bug fixing` 🪓 <br><br><br><br><br>
<i>Happy trading!<br><br>
And remember...</i>
***
> `"TIME IN THE MARKET IS BETTER THAN TIMING THE MARKET!"` <b><i>- Kenneth Fisher</i></b><br>
