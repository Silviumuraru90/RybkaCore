#!/usr/bin/env python3

# built-in and third-party libs
import os, time, requests

# custom libs
from custom_modules.logging.logging import log


running_in_ci = os.environ.get("CI", False)
runs = 0

while True:
    log.INFO(" 📡 Rybka bot is being started...")
    time.sleep(2)
    #######################################################################
    #             Change below line to: os.system("rybka")                #
    #######################################################################
    status = os.system("python3 rybka.py")
    if status == 7:
        log.FATAL(f" 🔴 Rybka bot errored out with code [{status}].\n\nExit code '7' is a custom-set exit code within bot's mechanics. Manual action is required, both Rybka and restarter module are stopped.")
    else:
        log.WARN(f" 🟠 Rybka bot errored out with code [{status}], which is not a custom-hard-coded one. Proceeding to check internet availability...")
        internet_down = False
        for i in range(1, 11):
            log.INFO(" ")
            log.INFO(f" 🟣 Testing internet. Attempt [{i}/10]")
            try:
                r = requests.get("https://www.google.com")
                log.INFO(f" 🟢🔌 Could ping Google servers, internet should be on - response [{r.status_code}] returned")
                time.sleep(5)
                break
            except Exception as e:
                internet_down = True
                log.WARN(" 🟠🔌 Internet seems to not be available")
                log.INFO(" 🟣 Waiting 15 seconds and trying again")
                time.sleep(15)
        if not internet_down:
            log.INFO(" 🟣 Rybka did not catch the internet connection as being down. Hence it might've been a different cause of failure")
            log.INFO(" 🟣 Applying a 1-minute break and will restart Rybka bot afterwards!")
            time.sleep(60)
        else:
            log.INFO(" 🟢 Restart action sent.")
    runs+=1
    if running_in_ci and runs == 3:
        log.FATAL(" 🔴 This is a CI run. Breaking the process now after the 3 attempts.")
